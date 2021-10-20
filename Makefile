deploy:
	sam build

	sam package --s3-bucket ${DOL_BNK_BUCKET} \
		--output-template-file packaged-template.yaml  \
		--force-upload \
		--region us-east-1
		# --profile caveman

	$(info [+] Deploying 'dol-bnk-python-test')
	sam deploy \
		--template-file packaged-template.yaml \
		--stack-name dol-bnk-python-test \
		--s3-bucket ${DOL_BNK_BUCKET} \
		--capabilities CAPABILITY_IAM \
		--region us-east-1\
		--force-upload 
		# --profile caveman

delete:
	aws cloudformation delete-stack \
		--stack-name dol-bnk-python-test 
		# --profile caveman