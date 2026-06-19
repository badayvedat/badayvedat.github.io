
The forge we deserve
May 9, 2026
GitHub is having a tough time. Their uptime (or rather, lack thereof) has become a meme, they’re facing exponential usage growth thanks to AI, and now high-profile projects like Ghostty are moving away. Developers are starting to discuss what they want from an alternative.

I’m thankful for GitHub, but it’s clear which way the winds are blowing. I hope they can fix their stability issues, but this is also an opportunity for the open-source world to try something new. So, what’s next? There are a lot of Git forges out there. Some, like Forgejo, are pretty good. It’s reasonable to predict that many people will move to these, and the ecosystem will become more fragmented.

There are benefits to centralization, and losing these could be painful. I love that most dev tools I use have a GitHub integration, and there’s almost no friction when I want to open an issue in a GitHub project.

This will not be the case in a world of many distinct gitlab.foo.com and forgejo.bar.com instances. Or perhaps everyone moves to some hot-new-AI-first-forge, and then we go through the same cycle of enshittification in 10-20 years.

But we don’t have to live like this. Armin Ronacher puts it well: it should be harder for one company’s drift to become a cultural crisis for everyone else.

I think we already have a promising path ahead: a Git forge built on an open, interoperable protocol.

Specifically, today, this is Tangled. It’s built on the AT Protocol. The details are a little nerdy (I recommend this explainer if you’re interested) but here are the important parts:

Your data (e.g. your repos, the issues you open, the PR comments you write) live on a server you can self-host (or you can use a public, shared server).
A centralized app (like tangled.org itself) aggregates everyone’s data in one place.
It’s all open-source, so if the Tangled devs start veering off course, we can fork it.
In other words: we get the benefits of a centralized service, and the benefits that come from owning our own data. You don’t need a million logins and you can still search everyone’s repos from a single search bar, but you also don’t have to entrust the Tangled people with eternal stewardship of your code.

The best part of this, in my eyes, is that it is structurally resistant to the lock-in that’s burning us with GitHub. Anyone can run their own Tangled fork, should they wish to. As long as the fork remains compatible with the Tangled schema (called a lexicon in ATProto parlance), then it doesn’t matter whether someone reads their profile from tangled.org or tangled-but-better.org or even tangled-but-with-some-crazy-different-ui-and-features.com. A good, early example of this openness is Mitchell Hashimoto’s tack — it lets you use other CI providers within Tangled if you don’t like their native Nix-flavored thing.

I want Tangled to do well. Today, it’s alpha software, so some things are rough around the edges — but it’s definitely usable for open-source work. They’ve raised a seed round, natively support jujutsu and stacked PRs, and just introduced an interesting web of trust implementation.

From what I’ve seen, it’s the only forge doing something fundamentally different to GitHub. The next forge should be a step up, not sideways. I’m starting all my new projects on Tangled, and I encourage you to try it.

Get new posts delivered to your inbox.
