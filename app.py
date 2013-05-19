from flask import Flask, render_template, request
from deshi import DEShi

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():

	if request.form:
		try:

			key = request.form['key']
			message = request.form['message']

			if not key or not message:
				raise Exception("Please fill in all fields!")

			app.logger.info("Key: %s" % key)
			app.logger.info("Message: %s" % message)

			deshi = DEShi(key, message)

			if request.form['type'] == "Encrypt":
				# encryption
				app.logger.info("Requesting encryption")

				# call encryption method on deshi
				deshi.encrypt()

				cypher = deshi.cyphertext

				print cypher

			#######################################################

			else:
				# decryption
				app.logger.info("Requesting decryption")

				cypher = message

				# call the decryption method on deshi
				deshi.decrypt()

				message = deshi.plaintext

				print message

		except:
			raise

	return render_template("index.html", **locals())

if __name__ == "__main__":
	app.run(debug=True)