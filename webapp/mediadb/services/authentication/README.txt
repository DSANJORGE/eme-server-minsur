# Step 1: request a code (emails it; also writes it to the templogincode table)
curl -s -X POST "http://localhost:8080/finder/mediadb/services/authentication/sendusercode.json" \
  --data-urlencode "email=<a real user's email>"
response:
{
	"response": {
		"status": "ok",
		"email": "support@openedit.org"
	}
}

# Step 2: redeem the 6-digit code from that email within 15 minutes
curl -s -X POST "http://localhost:8080/finder/mediadb/services/authentication/token.json" \
  --data-urlencode "grant_type=otp" \
  --data-urlencode "email=<same email>" \
  --data-urlencode "code=<6-digit code from the email>"


response:
{
	"access_token": "adminmd5421c0af185908a6c0c40d50fd5e3f16760d5580bctstamphe17GMyLCG7rsInbT5qIGQ==",
	"token_type": "Bearer",
	"expires_in": 86400,
	"refresh_token": "adminmd5421c0af185908a6c0c40d50fd5e3f16760d5580bc",
	"user": {
		"id": "admin",
		"firstname": "The",
		"lastname": "Administrator",
		"email": "support@entermediadb.org",
		"screenname": "Admin",
		"assetportrait": "http://localhost.com:8080/site/mediadb/services/module/asset/generated/Users/Shakil.A/image_picker_E3FCF644-58ED-4EFE-AFA7-CEC8386DF770-47636-000000A8B34B33E9.jpg/image200x200.webp"
	}
}