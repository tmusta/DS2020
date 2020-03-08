import numpy as np

def f(problem, answer):
    loss = 0.0
    for v, x in zip(problem, answer):
        #print(v,x)
        for n, c in enumerate(v):
            #print(x, c, c*np.power(x, len(v)-n-1))
            loss += c*np.power(x, len(v)-n-1)

    #exit()
    return loss

def mate(x1, x2):
    a = np.minimum(x1, x2)
    b = np.maximum(x1, x2)
    c = np.random.random()
    #return np.add(x1, np.add(x2,x1)*c)
    return a + (b-a)*c

def mutate(x, rng):
    c = 2*rng*np.random.random(x.shape)-rng
    return x + c

def iteration(p, xs):
    losses = np.array([[x, f(p, x)] for x in xs])
    best = xs[np.argsort(np.abs(losses)[:,1])][:5]
    new_xs = [x for x in best]
    for j in range(len(best)-1):
        for k in range(j+1, len(best)):
            new_xs.append(mate(best[j], best[k]))
    if np.random.rand() < 0.3:
        n = np.random.randint(0,len(new_xs))
        new_xs[n] = mutate(new_xs[n], 1)
        print(best, f(p, best[0]), '*')
    else:
        print(best, f(p, best[0]))
    xs = np.array(new_xs)
    return xs, f(p, best[0])

def generate_problem(deg=2, var=3, rng=100):
    return 2*rng*np.random.random((var,deg)) - rng 

def generate_solution(batch=15, var=3, rng=100):
    return 2*rng*np.random.random((batch, var)) - rng

if __name__=="__main__":
    batch = 15
    epochs = 10
    rng = 100
    deg = 3
    var = 1
    #p = np.array([[0.5, -3, 2], [0.5, -3, 3], [0.5, -3, 3], [0.5, -3, 3]])
    p = generate_problem()

    xs = generate_solution()
    
    for i in range(epochs):
    
        losses = np.array([[x, f(p, x)] for x in xs])
        best = xs[np.argsort(np.abs(losses)[:,1])][:5]
        new_xs = [x for x in best]
        for j in range(len(best)-1):
            for k in range(j+1, len(best)):
                new_xs.append(mate(best[j], best[k]))
        if np.random.rand() < 0.3:
            n = np.random.randint(0,len(new_xs))
            new_xs[n] = mutate(new_xs[n], 1)
            print(i, best, f(p, best[0]), '*')
        else:
            print(i, best, f(p, best[0]))
        xs = np.array(new_xs)
        
    
