from flask import Flask, render_template, request
app = Flask(__name__)

KEYLEN = 16

# tools
def chunks(string, length):
	# produce length-character chunks from string
	for i in range(0, len(string), length):
		yield string[i:i+length]

# main routine

@app.route("/", methods=['GET', 'POST'])
def index():

	if request.form:
		# gather data from post request
		message = request.form['message']
		key = request.form['key']

		# check for valid keylen
		if len(key) != KEYLEN:
			raise Exception("The key has to be exactly 16-bit!")

		app.logger.debug("Message: %s, key: %s" % (message, key))

		# split message into 16-bit chunks
		message_chunks = []
		for chunk in chunks(message, KEYLEN):
			message_chunks.append(chunk)

		app.logger.debug("Message in chunks of %d-bit:" % KEYLEN)
		app.logger.debug(message_chunks)



	return render_template("index.html", **locals())

if __name__ == "__main__":
    app.run(debug=True)