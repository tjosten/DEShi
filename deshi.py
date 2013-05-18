from flask import Flask, render_template, request
import binascii
app = Flask(__name__)

KEYLEN = 16

# tools
def to_binary(string):
	# convert every letter into its ascii number
	binary = []
	for s in string:
		binary.append(bin(ord(s))[2:].zfill(8))

	return ''.join(i for i in binary)

def to_ascii(binary):
	# binary is a binary with len 16-bit
	# so we devide it in 2 binarys with len 8-bit
	bin1 = binary[:8]
	bin2 = binary[8:]
	return "%s%s" % (chr(int(bin1, 2)), chr(int(bin2, 2)))

def chunks(string, length):
	# produce length-character chunks from string
	for i in range(0, len(string), length):
		yield string[i:i+length]

# template filters
@app.template_filter("to_ascii")
def template_to_ascii(binary):
	return to_ascii(binary)

# main routine
@app.route("/", methods=['GET', 'POST'])
def index():

	if request.form:
		# gather data from post request
		message = request.form['message']
		key = request.form['key']
		key_binary = to_binary(key)
		message_binary = to_binary(message)

		app.logger.debug("Message: %s (%s), key: %s (%s)" % (message, message_binary, key, key_binary))

		# check for valid keylen (add binary prefix b to binary key length)
		if len(key_binary) != KEYLEN:
			raise Exception("The key has to be exactly 16-bit!")

		# split message into 16-bit chunks
		message_chunks = []
		for chunk in chunks(message_binary, KEYLEN):
			message_chunks.append(chunk.zfill(KEYLEN))

		app.logger.debug("Message in chunks of %d-bit:" % KEYLEN)
		app.logger.debug(message_chunks)

	return render_template("index.html", **locals())

if __name__ == "__main__":
    app.run(debug=True)