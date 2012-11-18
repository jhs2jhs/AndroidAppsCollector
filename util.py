import time

def sleep_i(i):
    time.sleep(i)

def sleep():
    sleep_i(1)

def sleep_test():
    for i in range(1, 10):
        print i
        sleep()

## use to print the percent of progress 
def p_percent(p, i, i_t, percent):
    if i >= int(i_t*p/100):
        print '\t'+str(p)+'%'+'..'
        p = p + percent
    i = i + 1
    return p, i

def p_percent_copy(p, i, i_t, percent, db):
    if i >= int(i_t*p/100):
        print '\t'+str(p)+'%'+'..'
        p = p + percent
        db.commit()
    i = i + 1
    return p, i
