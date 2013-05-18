from flask import Flask, render_template, request
import binascii
app = Flask(__name__)

KEYLEN = 16
IP = [10, 6, 14, 2, 8, 16, 12, 4, 1, 13, 7, 9, 5, 11, 3, 15]
IP_REVERSE = [9, 4, 15, 8, 13, 2, 11, 5, 12, 1, 14, 7, 10, 3, 16, 6]

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

# permutation with chunks and IP parameter
def permutation(chunks, ip):
	permutated_chunks = [0] * len(chunks)
	for run, chunk in enumerate(chunks):
		permutated_chunk = [0] * len(chunk)
		for index, value in enumerate(chunk):
			new_index = ip[index]
			permutated_chunk[index] = chunk[new_index-1]
		permutated_chunks[run] = ''.join(i for i in permutated_chunk)
	return permutated_chunks

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

		# do the initial permutation
		permutated_message_chunks = permutation(message_chunks, IP)
		app.logger.debug("Message in permutated chunks of %d-bit:" % KEYLEN)
		app.logger.debug(permutated_message_chunks)

		# check if unpermutation works
		unpermutated_message_chunks = permutation(permutated_message_chunks, IP_REVERSE)
		if unpermutated_message_chunks != message_chunks:
			raise Exception("Permutation and then unpermutation did not return the initual message chunks!")

	return render_template("index.html", **locals())

if __name__ == "__main__":
    app.run(debug=True)