# India Professional Skills Intelligence Dataset

## Overview

This dataset contains 12,000 synthetic professional profiles representing India's
workforce, built to support research and learning around employability, skills demand,
salary patterns, and career progression across Indian states and industries.

Every value in this dataset is generated, not collected from any real person or any real
platform. This is stated plainly and upfront because the dataset's value depends on that
honesty being clear from the start. What makes it useful despite being synthetic is that
its structure, distributions, and correlations are calibrated against real, cited, publicly
available labor market statistics, so the patterns you find in it reflect genuine trends in
India's job market rather than arbitrary or convenient numbers.

## Why this dataset was built this way

Real, individual-level professional profile data of this kind is not available through any
free or public API. Building it by collecting real profiles from any professional networking
platform would violate that platform's terms of service. Rather than skip the idea or fake
its origins, this dataset takes the more honest path: real statistics from published labor
market research were used to shape every distribution, so the dataset behaves like the real
world even though no single row in it corresponds to a real person.

## What grounds this dataset in reality

The following figures come directly from published 2026 labor market research and were used
to calibrate the dataset's distributions:

- National employability calibrated to 56.35 percent, matching the India Skills Report 2026
  published by Wheebox in partnership with CII, AICTE, and AIU, based on more than 100,000
  respondents
- Uttar Pradesh, Maharashtra, and Karnataka are overrepresented among profile locations,
  matching the same report's finding that these three states currently lead the country in
  employability
- Artificial intelligence, data analytics, cloud computing, and cybersecurity are modeled as
  the most in demand skill areas, consistent with NASSCOM and India Skills Report findings,
  while remaining a minority of overall profiles, reflecting the genuine gap between demand
  for these skills and their supply in the workforce
- Generative AI tool usage is calibrated near the widely reported figure of over 90 percent
  adoption among Indian employees, with realistic variation by profession rather than one
  flat number applied to everyone
- The gig and freelance workforce is represented as a real but still modest share of
  profiles, consistent with current reporting on its growth

## What is inside

The dataset includes 26 columns covering job title, seniority level, industry, primary
skill area, a list of top skills, years of experience, education, city and state, company
size, employment type, work mode, generative AI tool usage, certifications, endorsements,
connection count, profile completeness, openness to work, last profile update, estimated
salary, an employability score, and whether a profile sits in a currently in demand skill
area.

Only two of these columns are engineered from the others. The remaining twenty four are raw
attributes. This is intentional. Feature engineering is left largely undone so that anyone
working with this dataset has real room to build their own features rather than finding
everything already decided for them.

## Suggested uses

This dataset supports a wide range of learning and research goals, including salary
prediction, employability modeling, skills gap analysis by region or industry, exploring how
education and certifications relate to career outcomes, and general practice with feature
engineering, classification, and regression on realistic tabular data.

It is well suited for students and early career data scientists who want a dataset that
feels close to real world workforce data without any of the access or licensing barriers
that come with real platform data, and for anyone researching India's labor market patterns
at a conceptual level.

## Limitations, stated honestly

This is a synthetic dataset. Exact individual values, such as one specific profile's salary
or employability score, should never be treated as a real observation. Only the aggregate
patterns and calibrated proportions are meant to reflect real world trends. Geographic
coverage is limited to twenty major Indian cities rather than the full range of India's
urban and rural workforce, and the skill lists provided per profession are illustrative
rather than exhaustive.

## Sources referenced for calibration

India Skills Report 2026, Wheebox, in partnership with CII, AICTE, and AIU.
NASSCOM workforce and skills reporting, 2026.

## A note on trust

Every effort was made to make this dataset earn trust honestly rather than by implying it is
something it is not. If you have questions about how any specific column or distribution was
built, please ask in the discussion section. Feedback and suggestions for improving the
realism or usefulness of this dataset are genuinely welcome.