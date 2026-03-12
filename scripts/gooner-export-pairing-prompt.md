# prompt for gooner — export pairing data

copy-paste this into your hermes chat to complete the backup:

---

```
i need you to export your telegram/whatsapp pairing data to the repo so we have a complete backup.

1. go to the repo:
   cd ~/goon && git pull origin main

2. copy pairing data:
   mkdir -p hermes/pairing
   cp ~/.hermes/pairing/*.json hermes/pairing/ 2>/dev/null
   ls -la hermes/pairing/

3. also grab the document cache listing (optional but useful):
   ls ~/.hermes/document_cache/ > hermes/document-cache-listing.txt 2>/dev/null

4. apply the new gooner personality config:
   cp hermes/config.yaml ~/.hermes/config.yaml
   echo "config updated — personality is now 'gooner' instead of 'kawaii'"

5. commit and push:
   cd ~/goon
   git add hermes/pairing/ hermes/document-cache-listing.txt
   git commit -m "export pairing data + apply gooner personality config"
   git push origin main

6. verify personality switch:
   grep 'personality:' ~/.hermes/config.yaml

tell me what the personality line says after the update.
```
