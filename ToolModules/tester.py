'''
Created on May 2, 2014

@author: kwalker
'''
import fields

outtest = fields.Output()

print outtest.getFields()
x = outtest.getFields()
x = list(x)
x.append("sdfsdf")
print x