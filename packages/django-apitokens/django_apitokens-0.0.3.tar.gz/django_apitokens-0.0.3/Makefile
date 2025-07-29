.PHONY: style
style:
	black --target-version=py311 \
	      --line-length=120 \
		  --skip-string-normalization \
		  apitokens testapp && \
	ruff check --fix apitokens testapp
	
check_style:
	black --target-version=py311 \
	      --line-length=120 \
		  --skip-string-normalization \
		  --check \
		  apitokens testapp && \
	ruff check apitokens testapp

build_lib:
	pip install .
	