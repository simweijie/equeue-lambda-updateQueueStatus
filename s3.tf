terraform {
  backend "s3" {
    bucket = "nus-iss-equeue-terraform"
    key    = "lambda/updateQueueStatus/tfstate"
    region = "us-east-1"
  }
}
