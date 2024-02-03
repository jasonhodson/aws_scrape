import subprocess
import os
import shutil

ecr_repository = "web_scrape_goodreads"
docker_tag = ecr_repository.replace("_", "")
lambda_functions = [
    "web_scrape_quote_goodreads",
    "web_scrape_group_goodreads"]
aws_account_id = "624562008531"

def run_command(command, suppress_output=False):
    if suppress_output:
        with open(os.devnull, 'w') as devnull:
            process = subprocess.run(command, shell=True, check=True, stdout=devnull, stderr=devnull)
    else:
        process = subprocess.run(command, shell=True, check=True)
    return process

def main():

    # SAM Build
    run_command(f"sam build -t template.yaml")

    # Docker Tag
    run_command(f"docker tag {docker_tag}:latest {aws_account_id}.dkr.ecr.us-east-2.amazonaws.com/{ecr_repository}:latest")

    # Docker Login to ECR
    run_command(f"aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin {aws_account_id}.dkr.ecr.us-east-2.amazonaws.com")

    # Docker Push
    run_command(f"docker push {aws_account_id}.dkr.ecr.us-east-2.amazonaws.com/{ecr_repository}:latest")

    # Docker Prune
    run_command("docker image prune -a -f")

    # Update Lambda Functions
    for lambda_function in lambda_functions:
        run_command(
            f"aws lambda update-function-code --function-name {lambda_function} --image-uri {aws_account_id}.dkr.ecr.us-east-2.amazonaws.com/{ecr_repository}:latest",
            suppress_output=True
        )

if __name__ == "__main__":
    main()