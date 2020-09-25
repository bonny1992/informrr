IMAGE := bonny1992/informrr
$(eval RELEASE = $(shell chmod +x .travis/get_release.sh && .travis/get_release.sh))

echo:
	@echo RELEASE is $(RELEASE)

test:
	true

image:
	docker build -t $(IMAGE):latest -t $(IMAGE):$(RELEASE) .

push-image:
	docker push $(IMAGE):$(RELEASE)
	docker push $(IMAGE):latest


.PHONY: all image push-image test