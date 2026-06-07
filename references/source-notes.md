# Source notes

This skill is an independent material-driven workflow inspired by public writing and rebuttal resources. Do not copy long external prompts verbatim into user work. Use the distilled procedures below.

## Public sources used during creation

- Leey21, `awesome-ai-research-writing`: https://github.com/Leey21/awesome-ai-research-writing
- runtsang, `RebuttalStudio`: https://github.com/runtsang/RebuttalStudio
- OpenAI skill creator guidance from the local `$skill-creator` skill.
- Existing local reference skills for paper writing, humanized editing, and academic plotting.
- Official venue pages should be checked live when current rules matter:
  - Science Robotics author information: https://www.science.org/journal/scirobotics
  - IEEE Robotics and Automation Letters: https://www.ieee-ras.org/publications/ra-l
  - IEEE Transactions on Robotics: https://www.ieee-ras.org/publications/t-ro
  - ICRA conference site: https://www.ieee-icra.org/

## Distilled patterns

From writing prompt collections:

- Treat writing as multiple tasks: abstract, introduction, related work, method, experiments, captions, cover letters, and rebuttal.
- Use structured prompts, but bind them to project evidence.
- Maintain clear output contracts so the assistant returns usable prose, not meta-advice.

From rebuttal workflows:

- Break reviewer comments into atomic issues before drafting.
- Assign response strategy per issue.
- Ground each response in evidence or a concrete revision.
- Keep tone respectful and concise.

From de-AI editing guidance:

- Detect clusters of formulaic phrasing rather than isolated words.
- Preserve meaning and technical register.
- Remove generic significance inflation and chatbot-like transitions.

From academic plotting workflows:

- Use deterministic code for numerical figures.
- Export vector graphics.
- Keep captions evidence-bearing and self-contained.

From venue, reproducibility, and disclosure guidance:

- Keep current page limits, templates, anonymity, AI-use, and submission rules out of static prose unless verified from official venue pages during the task.
- Use compact venue packs to steer tone and evidence expectations.
- Use scripts for repeatable checks such as citation-key coverage and risky scientific claim terms.

## Citation and provenance rule

When using external resources to write a paper:

- Cite scientific sources only when they are relevant to the manuscript's claims.
- Do not cite prompt repositories or this skill in the paper unless the authors intentionally discuss writing assistance.
- Follow the venue's AI-assistance disclosure policy.
