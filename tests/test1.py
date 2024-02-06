import math 
# a = math.ceil(0.55)
# print(a)
# frac_str = '1/255'


# num, denom = frac_str.split('/')
# print(num)
# print(denom)
# frac = (float(num) / float(denom))*100
# if frac < 1 :
#    print('1%') 

# frac_str = "1/255"

def percentage(frac_str):
	num, denom = frac_str.split('/')
	output = (float(num) / float(denom))*100
   if output < 1:
      frac = 1
            # print('1%')
         # else:
         #    frac = round(frac,0) + '%'
      return frac
   else:
      return 'NA'
	

result = percentage("1/255")
print(result)
result = percentage("10/255")
print(result)