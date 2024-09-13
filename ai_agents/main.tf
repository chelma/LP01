provider "aws" {
  region = "us-west-2"
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "esi_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

# Attach the basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda function definition
resource "aws_lambda_function" "esi" {
  filename         = "ai_agents.zip"
  function_name    = "esi"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handlers.esi_handler"
  source_code_hash = filebase64sha256("ai_agents.zip")
  runtime          = "python3.12"
  timeout          = 300
}

# Set up the Bedrock Agent
data "aws_caller_identity" "current" {}
data "aws_partition" "current" {}
data "aws_region" "current" {}

data "aws_iam_policy_document" "lp01_agent_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      identifiers = ["bedrock.amazonaws.com"]
      type        = "Service"
    }
    condition {
      test     = "StringEquals"
      values   = [data.aws_caller_identity.current.account_id]
      variable = "aws:SourceAccount"
    }
    condition {
      test     = "ArnLike"
      values   = ["arn:${data.aws_partition.current.partition}:bedrock:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:agent/*"]
      variable = "AWS:SourceArn"
    }
  }
}

data "aws_iam_policy_document" "lp01_agent_permissions" {
  statement {
    actions = ["bedrock:InvokeModel"]
    resources = [
      "arn:${data.aws_partition.current.partition}:bedrock:${data.aws_region.current.name}::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
    ]
  }
}

resource "aws_iam_role" "lp01_agent_role" {
  assume_role_policy = data.aws_iam_policy_document.lp01_agent_trust.json
  name_prefix        = "AmazonBedrockExecutionRoleForAgents_"
}

resource "aws_iam_role_policy" "lp01_agent_policy" {
  policy = data.aws_iam_policy_document.lp01_agent_permissions.json
  role   = aws_iam_role.lp01_agent_role.id
}

resource "aws_bedrockagent_agent" "lp01_agent" {
  agent_name                  = "lp01-agent"
  agent_resource_role_arn     = aws_iam_role.lp01_agent_role.arn
  idle_session_ttl_in_seconds = 500
  foundation_model            = "anthropic.claude-3-5-sonnet-20240620-v1:0"
  instruction                 = "You are an efficient, practical assistant whose role is to provide succint and precise answers to the user.  You specialize in knowledge about the EVE Online universe and are able to use tools to retrieve answers to questions outside your training data."
}

# Set up the Bedrock Action Group
resource "aws_bedrockagent_agent_action_group" "lp01_action_group" {
  action_group_name          = "lp01_action_group"
  agent_id                   = aws_bedrockagent_agent.lp01_agent.agent_id
  agent_version              = "DRAFT"
  skip_resource_in_use_check = true
  action_group_executor {
    lambda = aws_lambda_function.esi.arn
  }
  api_schema {
    payload = file("openapi/esi_apis.json")
  }
}

# Permission for Bedrock to invoke the Lambda function
resource "aws_lambda_permission" "allow_bedrock_invoke" {
  statement_id  = "AllowBedrockInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.esi.function_name
  principal     = "bedrock.amazonaws.com"
  source_arn    = aws_bedrockagent_agent.lp01_agent.agent_arn
}