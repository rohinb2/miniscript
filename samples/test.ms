h = label(true, "high");
l = label(undefined, "high");
temp = true;
if (h)
  l = temp;
else 
  l = !temp;
labelPrint(h);
labelPrint(l);
labelPrint(temp);
