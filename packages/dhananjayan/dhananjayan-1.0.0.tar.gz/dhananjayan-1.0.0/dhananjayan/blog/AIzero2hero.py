def day1():
    return """
    TLDR: Started reading a diffusion-LLM paper and some probability theory. 

    Today, I decided that I was going to take a look at Diffusion-based LLMs. I have long been interested in it,
    ever since LLaDa came out and how Mercury and Gemini Diffusion claimed to be so much faster than AutoRegressive Counterparts.

    While I was reading the LLaDa paper, I was confused about several things. Initially, I saw something about Fisher
    Consistency which made me curious. The authors noted that Fisher's Consistency implied the ability to recover the true data distribution
    with infinite data, a sufficiently large network and optimal training. This struck me hard because a) If there is a mathematical
    foundation to this, I would NEED to learn it as it can be useful for theoretical proofs etc. b) They mentioned that 
    Fisher made this claim MORE THAN HUNDRED YEARS AGO(in 1922). 
 
    I found the paper, but it was too big so I started reading the wiki page instead for a brief introduction. It mentioned something
    about the Strong Law of Large Numbers. I remember reading about it in Probability class and being very confused as to what was the 
    difference b/w this and the Weak Law. So, I revisited it.

    It was very weird to me that the Strong Law used "almost surely" when it claims w.p(with probability) 1. Surely, if something has a 
    probability of 1, we should call it "Surely" and not "almost surely", right? Wrong. I quickly realized this was somewhat
    similar to the 3*0.33333 = 1, which equally bamboozled me. I vividly remember being so perplexed that I had to call my math teacher
    multiple times and ask about this.

    Anyways, I realized today that what is happening here is something similar. The probability of picking exactly 0.4(or any other real
    number for that matter) from a Uniform Distribution over [0,1] is... 0. In other words, the probability of not picking 0.4 is 1.
    However, that doesn't mean that 0.4 will not be picked "surely". We can only say "almost surely", which is exactly what the theorem claims.

    It was at this moment that I had realized the difficulties in extending probability theories to the Continuous case and how this was a direct result
    of the issues caused by that extension. I had failed to even notice that such a distinction should exist.

    Regarding the difference b/w weak and strong, notice how one of them is a limit inside a probability and the other one is the other way around.
    "And that made all the difference".

    The weak law talks about how the probability of deviation(from Mu) converges to 0. The strong law talks about the deviation itself converging to 0(w.p. 1).

    So if there are a million events, weak law tells the probability of going out of bound continues to decrease, but all of them could be non zero.
    So, it is entirely possible that all of them(in the infinite case, infinite of them) can be out of bound. The deviation can be more than epsilon. Just the pr of deviation keeps reducing.

    In the strong case, the deviation keeps decreasing and so you can only have finite deviations.

    I've also started reading the OG 2015 Paper titled "Deep Unsupervised Learning using Nonequilibrium Thermodynamics", which seems to have introduced the diffusion idea/concept
    into the ML World from Physics. Currently, I am unable to understand much, and that is where I am stopping today. Thanks for reading patiently. 
"""