def square(y):
  print("{} 的平方為 {}".format(y, y*y)) 


X = int(input("請輸入數字:"))
if (X==0):
	print("您輸入的是0")
elif (X>0):
	print("您輸入的是正數")
	for i in range(1,X+1,2):
		square(i)
else:
	print("您輸入的是負數")