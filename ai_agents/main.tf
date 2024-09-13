provider "aws" {
  region = "us-west-2"
}

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

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

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