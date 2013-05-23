from flask import Flask, render_template, request
from deshi import DEShi

# flask is a python microframework we use to serve the web app
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():

	error = False
	typ = ""

	if request.form:
		try:
			key = request.form['key']
			message = request.form['message']

			if not key or not message:
				raise Exception("Please fill in all fields!")

			if len(message) % 2 != 0:
				raise Exception("The message must be a multiple of 16-bit long!")

			app.logger.info("Key: %s" % key)
			app.logger.info("Message: %s" % message)

			if request.form['type'] == "Encrypt":
				typ = "encrypt"

				# encryption
				app.logger.info("Requesting encryption")

				# create new instance with key and message
				deshi = DEShi(key, message)

				# call encryption method on deshi
				deshi.encrypt()

				cypher = deshi.cyphertext

				# encode the cypher to hex so it can be displayed in the browser
				# without encoding errors
				cypher = cypher.encode('hex')

			#######################################################

			else:
				typ = "decrypt"
				# decryption
				app.logger.info("Requesting decryption")

				cypher = message

				# create new instance with key and hex-decoded cypher
				deshi = DEShi(key, cypher.decode('hex'))

				# call the decryption method on deshi
				deshi.decrypt()

				message = deshi.plaintext

		except Exception, e:
			# we naively catch all exceptions and threat them as a user error, like a boss.
			error = e

	try:
		return render_template("index.html", **locals())
	except UnicodeDecodeError:

		# if the template fails to render, the decryption key is most probably wrong
		# because the decrypted message contains illegal ascii characters
		# that's why we're listening for an UnicodeDecodeError exception here
		# (Flask is trying to convert everything to UTF-8)

		del message
		error = "The decrypted message contains illegal ascii characters which most probably means that your encryption key is invalid. Sorry."
		return render_template("index.html", **locals())

if __name__ == "__main__":
	app.run(debug=False, port=5556)