class DEShi(object):

	_KEYLEN = 16

	_IP = [10, 6, 14, 2, 8, 16, 12, 4, 1,
		13, 7, 9, 5, 11, 3, 15]

	_IP_INVERSE = [9, 4, 15, 8, 13, 2, 11, 5,
		12, 1, 14, 7, 10, 3, 16, 6]

	_EXPANSION = [8, 1, 2, 3, 4, 5,
		4, 5, 6, 7, 8, 1]

	_P = [6, 4, 7, 3,
		5, 1, 8, 2]

	_PC1 = [11, 15, 4, 13, 7, 9, 3, 2, 5, 14, 6, 10, 12, 1]

	_PC2 = [6, 11, 4, 8, 13, 3, 12, 5, 1, 10, 2, 9]

	_LEFT_ROTATIONS = [
		1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1
	]

	_SBOXES = [
		# S1
		[
			[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
			[0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
			[4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
			[15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
		],
		# S2
		[
			[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
		 	[3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
		 	[0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
		 	[13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
		]
	]

	_subkeys = [0] * 16

	def __init__(self, key, message):

		# check if key is 2 bytes (16 bit) long
		if len(key) != 2:
			raise ValueError("Key must be exactly 2 bytes (16 bit) long!")

		if len(message) == 0:
			raise ValueError("No message given!")

		self._key_ascii = key
		self._message_ascii = message

		# convert data to binary
		self._key = self._ascii_to_bits(key)

		# generate subkeys
		self._generate_subkeys()

	##############################################
	# private methods
	##############################################

	# returns a 16-bit list as ascii string of 2 characters
	def _bits_to_ascii(self, bits):
		# the result
		result = []
		position = char = 0

		# first 8 bit:
		first = bits[:8]
		last = bits[8:]

		first_string = [''] * len(first)
		last_string = [''] * len(last)

		# convert them to a string so we can parse them..
		i = 0
		while i < len(first):
			first_string[i] = str(first[i])
			i+=1
		first_string = eval('0b'+''.join(first_string))

		i = 0
		while i < len(last):
			last_string[i] = str(last[i])
			i+=1
		last_string = eval('0b'+''.join(last_string))

		#print first_string

		return "%s%s" % (chr(first_string), chr(last_string))

	# returns an ascii string as a bit list
	def _ascii_to_bits(self, ascii):

		# convert ascii chars to their representing numbers
		ascii_array = [ord(char) for char in ascii]

		# create the list to return
		# each character requires 8 bit
		result = [0] * (len(ascii) * 8)

		# create an 8-bit combination out of every character
		position = 0
		for char in ascii_array:
			i = 7
			while i >= 0:
				if char & (1 << i) != 0:
					result[position] = 1
				else:
					result[position] = 0
				position += 1
				i -= 1

		return result

	# generate subkeys from given key
	def _generate_subkeys(self):

		# permutate key
		key = self._permutate(self._key, self._PC1)

		# devide into left and right
		L = key[:7]
		R = key[7:]

		# calculate 16 subkeys
		i = 0
		while i < 16:
			# left shifts
			j = 0
			while j < self._LEFT_ROTATIONS[i]:
				L.append(L[0])
				del L[0]

				R.append(R[0])
				del R[0]

				j += 1

			# create the subkey from L and R with permutation PC2
			self._subkeys[i] = self._permutate(L + R, self._PC2)

			i += 1

	# permutation with given IP
	def _permutate(self, message, ip):

		print message
		if len(message) != 16:
			if type(message) == str:
				message = "00000000" + message
			else:
				message = [0] * 8 + message

		permutated_message = [0] * len(ip)
		for index, value in enumerate(permutated_message):
			new_index = ip[index]
			permutated_message[index] = int(message[new_index-1])
		return permutated_message

	# expansion with given IP
	def _expand(self, message, ip):
		expanded_message = [0] * len(ip)
		for index, value in enumerate(expanded_message):
			new_index = ip[index]
			expanded_message[index] = int(message[new_index-1])
		return expanded_message

	# the DEShi algo
	def _deshi(self, chunk, typ='encrypt'):

		# set type to encrypt or decrypt
		if typ == "encrypt":
			iteration = 0
		else:
			iteration = 15

		# first: devide the chunk in 8-bit party for L and R
		L = chunk[:8]
		R = chunk[8:]

		# the 16 rounds of DES..
		i = 0
		while i < 16:
			# save a temporary R because this original R will become L later
			temporary_R = R

			# expand R to 12 bit
			R = self._expand(R, self._EXPANSION)
			subkey = self._subkeys[iteration]

			# xor operation for the lists, the python way
			R = list(map(lambda e, key: e ^ key, R, subkey))

			# blocks of 2x6-bit for Sbox 1 and Sbox 2
			blocks = [R[:6], R[6:]]

 			# run the Sbox magic
 			sbox_results = [0] * len(blocks)
			j = 0
			while j < len(blocks):
				block = blocks[j]

				row = bin(block[0] + block[5])
				col = bin(block[1] + block[2] +  block[3] + block[4])

				# get correct integer value from sbox
				result = self._SBOXES[j][int(row, 2)][int(col, 2)]

				# save the result
				sbox_results[j] = result

				j += 1

			# now permutate the results with P
			R_tmp = 0
			for result in sbox_results:
				R_tmp += result

			# convert value to binary again, remove the b prefix and make it 8 bit
			result_binary = bin(R_tmp)[2:].zfill(8)
			R = self._permutate(result_binary, self._P)

			# and finally: XOR with L
			R = list(map(lambda r, l: r ^ l, R, L))

			# L becomes old R
			L = temporary_R

			i += 1
			if typ == "encrypt":
				iteration += 1
			else:
				iteration -= 1

		# done, final permutation
		final = self._permutate(R + L, self._IP_INVERSE)

		return final

	##############################################
	# public methods
	##############################################

	def encrypt(self):

		result = []

		# read ascii message in blocks of 16 bit
		i = 0
		while i < len(self._message_ascii):

			# convert ascii-message-chunk in bitlist
			message = self._ascii_to_bits(self._message_ascii[i:i+2])

			# permutate message
			data = self._permutate(message, self._IP)

			# call the deshi algo with parameter
			encrypted_data = self._deshi(data, 'encrypt')

			# append cypher text to result list, but convert it to ascii first
			result.append(self._bits_to_ascii(encrypted_data))
			# ok, we don't convert it to ascii as we're 8-bit here and 255 > 128, so we get illegal characters. we then use a binary cypher text.
			#result.append(encrypted_data)

			i += 2

		result_text = "".join(result)

		"""for r in result:
			for i in r:
				result_text += str(i)"""

		self.cyphertext = result_text

	def decrypt(self):

		result = []

		# read binary message in blocks of 16 bit
		i = 0
		while i < len(self._message_ascii):

			# convert ascii-message-chunk in bitlist
			message = self._ascii_to_bits(self._message_ascii[i:i+2])

			# permutate message
			data = self._permutate(message, self._IP)

			# call the deshi algo with parameter
			decrypted_data = self._deshi(data, 'decrypt')

			# append plain text to result list, but convert it to ascii first
			result.append(self._bits_to_ascii(decrypted_data))

			i += 2

		self.plaintext = ''.join(result)