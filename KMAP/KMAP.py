class KMAP(object):
	"""docstring for SLAP"""
	def __init__(self, Id_new=None, Id_old=None, k1_new=None, k2_new=None, k1_old=None, k2_old=None, Id=None):
		self.Id_new = Id_new
		self.Id_old = Id_old
		self.k1_new = k1_new
		self.k1_old = k1_old
		self.k2_new = k2_new
		self.k2_old = k2_old
		self.Id = Id


	def HammingWeight(self, x):
		return x.count("1")

	def rotate(self, string, hamming_weight):
		if len(string) == 0 or hamming_weight < 0 or hamming_weight > len(string):
			return ""

		if hamming_weight == 0:
			return string

		p1 = string[:hamming_weight]
		p2 = string[hamming_weight:]

		return p2+p1

	def rot_inv(self, string, hamming_weight):
		if len(string) == 0 or hamming_weight < 0 or hamming_weight > len(string):
			return ""

		if hamming_weight == 0:
			return string

		p1 = string[:-hamming_weight]
		p2 = string[-hamming_weight:]

		return p2+p1


	def stringXOR(self, a, b):
		result = ""
		for i in range(len(a)):
			if a[i] == b[i]:
				result += "0"
			else:
				result += "1"

		return result

	def pseudo_kasami_code(self,X, seed):
		l = len(X)
		a = l-seed
		p1 = X[:a]
		p2 = X[a:]
		Y = p2+p1
		K_c = self.stringXOR(X,Y)
		return K_c

	def UpdateKeys(self, Id_new, n1, n2, K1_s, K2_s):

		P = self.stringXOR(n1,n2)
		K = 64
		seed = self.HammingWeight(P)%K


		


		a = self.stringXOR(self.pseudo_kasami_code(Id_new,seed),n1)
		b = self.pseudo_kasami_code(n2,seed)

		self.k1_old = self.k1_new
		self.k2_old = self.k2_new
		self.Id_old = self.Id_new


		self.Id_new = self.rotate(a,self.HammingWeight(b))
		self.k1_new = self.pseudo_kasami_code(K1_s,seed)
		self.k2_new = self.pseudo_kasami_code(K2_s,seed)

	
	def CurrentState(self):
		print("Id_old = {}".format(self.Id_old))
		print("k1_old = {}".format(self.k1_old))
		print("k2_old = {}".format(self.k2_old))
		print("Id_new = {}".format(self.Id_new))
		print("k1_new = {}".format(self.k1_new))
		print("k2_new = {}".format(self.k2_new))


class Reader(KMAP):
	"""docstring for Reader"""

	def ComputeChallenge(self, n1, n2):
		P = self.stringXOR(n1,n2)
		K = 64
		seed = self.HammingWeight(P)%K

		A = self.rotate(self.rotate(n1,self.HammingWeight(self.stringXOR(Id_new,k1_new))),self.HammingWeight(k2_new))

		B = self.rotate(self.rotate(n2,self.HammingWeight(self.stringXOR(k2_new,Id_new))),self.HammingWeight(self.stringXOR(k1_new,n1)))

		K1_s = self.rotate(self.pseudo_kasami_code(k1_new,seed),self.HammingWeight(self.pseudo_kasami_code(n1,seed)))
		K1_s = self.stringXOR(K1_s,k2_new)

		K2_s = self.rotate(self.pseudo_kasami_code(k2_new,seed),self.HammingWeight(self.pseudo_kasami_code(n2,seed)))
		K2_s = self.stringXOR(K2_s,k1_new)

		a = self.stringXOR(self.pseudo_kasami_code(K2_s,seed),self.pseudo_kasami_code(n2,seed))
		b = self.rotate(self.pseudo_kasami_code(n1,seed),self.HammingWeight(a))
		c = self.stringXOR(self.pseudo_kasami_code(K1_s,seed),n2)
		C = self.rotate(b,self.HammingWeight(c))

		self.A = A
		self.B = B
		self.C = C
		self.n1 = n1
		self.n2 = n2

		return A,B,C

	def VerifyChallenge(self, D, seed):
		a = self.stringXOR(self.pseudo_kasami_code(Id,seed),self.pseudo_kasami_code(n1,seed))
		b = self.stringXOR(self.pseudo_kasami_code(Id_new,seed),self.pseudo_kasami_code(k1_new,seed))
		c = self.rotate(a,self.HammingWeight(b))
		d = self.pseudo_kasami_code(k2_new,seed)
		D_s = self.rotate(c,self.HammingWeight(d))



		if D_s == D:
			print("We win")
			K1_s = self.rotate(self.pseudo_kasami_code(k1_new,seed),self.HammingWeight(self.pseudo_kasami_code(n1,seed)))
			K1_s = self.stringXOR(K1_s,k2_new)

			K2_s = self.rotate(self.pseudo_kasami_code(k2_new,seed),self.HammingWeight(self.pseudo_kasami_code(n2,seed)))
			K2_s = self.stringXOR(K2_s,k1_new)
			self.UpdateKeys(self.Id_new, self.n1, self.n2, K1_s, K2_s)
			


class Tag(KMAP):
	"""docstring for Tag"""
	def ComputeChallenge(self, A, B, C):
		a = self.stringXOR(Id_new,k1_new)
		b = self.rot_inv(A,self.HammingWeight(k2_new))
		n1 = self.rot_inv(b,self.HammingWeight(a))

		p = self.stringXOR(k2_new,Id_new)
		q = self.stringXOR(k1_new,n1)
		r = self.rot_inv(B,self.HammingWeight(q))
		n2 = self.rot_inv(r,self.HammingWeight(p))

		P = self.stringXOR(n1,n2)
		K = 64
		seed = self.HammingWeight(P)%K

		K1_s = self.rotate(self.pseudo_kasami_code(k1_new,seed),self.HammingWeight(self.pseudo_kasami_code(n1,seed)))
		K1_s = self.stringXOR(K1_s,k2_new)

		K2_s = self.rotate(self.pseudo_kasami_code(k2_new,seed),self.HammingWeight(self.pseudo_kasami_code(n2,seed)))
		K2_s = self.stringXOR(K2_s,k1_new)

		a = self.stringXOR(self.pseudo_kasami_code(K2_s,seed),self.pseudo_kasami_code(n2,seed))
		b = self.rotate(self.pseudo_kasami_code(n1,seed),self.HammingWeight(a))
		c = self.stringXOR(self.pseudo_kasami_code(K1_s,seed),n2)
		C_s = self.rotate(b,self.HammingWeight(c))

		if C_s == C:
			print("So far so good")
			a = self.stringXOR(self.pseudo_kasami_code(Id,seed),self.pseudo_kasami_code(n1,seed))
			b = self.stringXOR(self.pseudo_kasami_code(Id_new,seed),self.pseudo_kasami_code(k1_new,seed))
			c = self.rotate(a,self.HammingWeight(b))
			d = self.pseudo_kasami_code(k2_new,seed)
			D = self.rotate(c,self.HammingWeight(d))

			return D




if __name__ == '__main__':
	import random
	# Reader sends hello
	# Tag sends Id_new

	# Reader side communication
	Id_new = bin(random.randint(2**15, 2**16))[2:]
	k1_new = bin(random.randint(2**15, 2**16))[2:]
	k2_new = bin(random.randint(2**15, 2**16))[2:]

	n1 = bin(random.randint(2**15, 2**16))[2:]
	n2 = bin(random.randint(2**15, 2**16))[2:]

	Id = '1111101111100101'

	# P = stringXOR(n1,n2)
	K = 64

	P = ""
	for i in range(len(n1)):
		if n1[i] == n2[i]:
			P += "0"
		else:
			P += "1"

	n = P.count("1")

	seed = n%K

	reader = Reader(Id_new=Id_new, k1_new=k1_new, k2_new=k2_new, Id=Id)
	A, B, C = reader.ComputeChallenge(n1,n2)

	tag = Tag(Id_new=Id_new, k1_new=k1_new, k2_new=k2_new, Id=Id)
	D = tag.ComputeChallenge(A, B, C)

	reader.VerifyChallenge(D,seed)

	reader.CurrentState()
	print()
	tag.CurrentState()

