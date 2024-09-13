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

  environment {
    variables = {
      EVE_REST_URL = "https://esi.evetech.net/latest/"
    }
  }
}

# Permission for Bedrock to invoke the Lambda function
resource "aws_lambda_permission" "allow_bedrock_invoke" {
  statement_id  = "AllowBedrockInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.esi.function_name
  principal     = "bedrock.amazonaws.com"
  source_arn    = "arn:aws:bedrock:us-west-2:729929230507:agent/PNIDRKHN5C"
}
