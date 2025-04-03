# main
# helper stuff what i can not type for some reason : {} ; []

def log_data(a):
	print(a);

log_data("a");

def get_bigger(x):
	return x+1;

print(f"{get_bigger(1)} is bigger than {1}");

# some stuff i saw in the web as a "hard thing"
def contains_num(orderedArray, num):
	leng = len(orderedArray) -1;
	if orderedArray[0]>num:
		return False;
	elif orderedArray[leng]<num:
		return False;

	for x in range(leng):
		if orderedArray[x]==num:
			return True;

	return False;




gg = [0,1,2,3,5,6];

log_data(contains_num(gg,-1));
log_data(contains_num(gg,10));
log_data(contains_num(gg,5));
log_data(contains_num(gg,2));
log_data(contains_num(gg,4));


#def convert_type(x,to):
#	if type(to)!=string:
#		if type(x) == int:
#			return float(x);
#		else:
#			return int(x);
#
#apple = "10";
#apple = convert_type(apple,None);
#log_data(apple);

imp = input("you alive? ");
log_data(f"Nice {imp}");



















input("Hit enter to close");