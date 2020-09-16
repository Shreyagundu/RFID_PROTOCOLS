from flask import Flask
import json
from flask import request
import random
from flask import jsonify

app = Flask(__name__)
print("__name__ is ", __name__)

w = 'win'
l ='lose'


class SLAP(object):
	"""docstring for SLAP"""
	def __init__(self, Id_new=None, Id_old=None, k1_new=None, k2_new=None, k1_old=None, k2_old=None, threshold=None):
		self.Id_new = Id_new
		self.Id_old = Id_old
		self.k1_new = k1_new
		self.k1_old = k1_old
		self.k2_new = k2_new
		self.k2_old = k2_old
		self.threshold = threshold


	def HammingWeight(self, x):
		return x.count("1")

	def HammingWeightOptimized(self, x):
	    x -= (x >> 1) & 0x5555555555555555
	    x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
	    x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0f
	    return ((x * 0x0101010101010101) & 0xffffffffffffffff ) >> 56

	def GroupingRoutine(self, target, a, begin, length, threshold):
		if (length-begin) <= threshold:
			if begin not in target:
				target.append(begin)

			if length not in target:
				target.append(length)
			return
		w = self.HammingWeight(a[begin:length])
		self.GroupingRoutine(target, a, begin, length-w, threshold)
		self.GroupingRoutine(target, a, length-w, length, threshold)

						

	def split(self, target, a):
		split_ret = []
		for i in range(len(target)-1):
			split_ret.append(a[target[i]: target[i+1]])
		return split_ret

	def rotate(self, string, hamming_weight):
		if len(string) == 0 or hamming_weight < 0 or hamming_weight > len(string):
			return ""

		if hamming_weight == 0:
			return string

		p1 = string[:hamming_weight]
		p2 = string[hamming_weight:]

		return p2+p1

	def rotateALL(self, list_substr):
		temp = ""
		for sub in list_substr:
			temp += self.rotate(sub, self.HammingWeight(sub))

		return temp

	def stringXOR(self, a, b):
		result = ""
		for i in range(len(a)):
			if a[i] == b[i]:
				result += "0"
			else:
				result += "1"

		return result


	def Grouping(self, a, t):
		target = []
		self.GroupingRoutine(target, a, 0, len(a), t)
		return target

	def UpdateKeys(self, B, n, Blr, Clr):
		self.k1_old = self.k1_new
		self.k2_old = self.k2_new
		self.Id_old = self.Id_new

		self.k1_new = self.stringXOR(self.Conv(self.k1_old, n, ), self.k2_old)
		self.k2_new = self.stringXOR(self.Conv(self.k2_old, B), self.k1_old)
		self.Id_new = self.Conv(self.Id_old, self.stringXOR(n, Blr+Clr))

	def CurrentState(self):
		print("Id_old = {}".format(self.Id_old))
		print("k1_old = {}".format(self.k1_old))
		print("k2_old = {}".format(self.k2_old))
		print("Id_new = {}".format(self.Id_new))
		print("k1_new = {}".format(self.k1_new))
		print("k2_new = {}".format(self.k2_new))
		


	def Conv(self, a, b, threshold=None):
		if threshold is None:
			threshold = self.threshold
		target_a = self.Grouping(a, threshold)
		target_b = self.Grouping(b,threshold)
		# print(target_a)
		# print(target_b)

		rearrange_a = self.split(target_b, a)
		rearrange_b = self.split(target_a, b)
		# print(rearrange_a)
		# print(rearrange_b)

		final_a = self.rotateALL(rearrange_a)
		final_b = self.rotateALL(rearrange_b)
		# print(final_a)
		# print(final_b)
		return self.stringXOR(final_a, final_b)
		# return bin(int(final_a, 2) ^ int(final_b, 2)) [2:]

class Reader(SLAP):
	"""docstring for Reader"""

	def ComputeChallenge(self, n):
		A = self.Conv(self.k1_new, self.k2_new, self.threshold)
		A = self.stringXOR(A, n)

		a = self.rotate(self.k1_new, self.HammingWeight(n))
		b = self.Conv(self.k2_new, self.stringXOR(self.k2_new, n), self.threshold)
		c = self.rotate(b, self.HammingWeight(self.k1_new))
		d = self.Conv(a, self.stringXOR(self.k1_new, self.k2_new), self.threshold)

		B = self.stringXOR(c, d)

		if self.HammingWeight(B) %2:
			B_send = B[len(B)//2:]
		else:
			B_send = B[:len(B)//2]

		self.A = A
		self.B = B
		self.Blr = B_send
		self.n = n

		return A, B_send

	def VerifyChallenge(self, Clr):
		a = self.Conv(self.B, self.k1_new, self.threshold)
		b = self.Conv(self.k1_new, self.stringXOR(self.k2_new, self.n), self.threshold)
		c = self.Conv(a, b, self.threshold)
		C = self.stringXOR(c, self.Id_new)

		if self.HammingWeight(C) % 2:
			C_recv = C[len(C)//2:]
		else:
			C_recv = C[:len(C)//2]

		if C_recv == Clr:
			# print("We win")
			self.UpdateKeys(self.B, self.n, self.Blr, Clr)
			return w





Id_new = '0'
threshold = 6
k1_new = '1101011111011000'
k2_new = '1101000010100100'
n = bin(random.randint(2**15, 2**16))[2:]



@app.route('/ID', methods=['GET', 'POST'])
def ID():
	if request.method == "POST":
		global Id_new
		Id_new = request.form.get('Id_new')
		# print(Id_new)
		ret = {'Id_new': Id_new}
		return ret

@app.route('/values', methods=['GET'])
def values():
	# print(Id_new)
	# global Id_new
	global reader
	reader = Reader(Id_new=Id_new, k1_new=k1_new, k2_new=k2_new, threshold=threshold)
	A, B_send = reader.ComputeChallenge(n)
	val = {'A' : A ,'B_send':B_send,'Id_new': Id_new}
	return val


@app.route('/verify', methods=['GET', 'POST'])
def verification():
	if request.method == "POST":
		global C
		C = request.form.get('C')
		v=reader.VerifyChallenge(C)
		if(v=='win'):
			ret = {'state':"we win!!! Wohooo"}
			reader.CurrentState()
			return ret




if __name__ == '__main__':
    app.run(host='localhost', port="5000")