provider "aws" {
  region = "us-east-2"
}

resource "aws_instance" "ec1"{
  ami           = "ami-0416962131234133f"  # Example AMI ID for us-east-2 (Amazon Linux 2)
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance-1"
  }
}

resource "aws_instance" "ec4" {
  ami           = "ami-0416962131234133f"  # Example AMI ID for us-east-2 (Amazon Linux 2)
  instance_type = "t3.medium"

  tags = {
    Name = "example-instance-2"
  }
}
