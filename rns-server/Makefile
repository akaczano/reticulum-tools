rns-node:
	docker image build -t rns-node -f docker/rns_node.df .

messenger-node: rns-node
	docker image build -t messenger-node -f docker/messenger_node.df .

clean-db:
	rm -f tests/db/*.db
	touch tests/db/gordon.db
	touch tests/db/todd.db
	touch tests/db/roger.db
clean-rns:
	rm -rf tests/configs/gordon/interfaces
	rm -rf tests/configs/gordon/storage
	rm -rf tests/configs/todd/interfaces
	rm -rf tests/configs/todd/storage
	rm -rf tests/configs/transport/storage
	rm -rf tests/configs/transport/interfaces
	rm -rf tests/configs/roger/interfaces
	rm -rf tests/configs/roger/storage
clean: clean-db clean-rns
