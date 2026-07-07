# Search Measurement Reference
Use this for baselines, Search Console, analytics, migrations, launches, traffic-loss diagnosis, experiments, and generative-search reporting.

## Measurement Contract
Before recommending a change, define:

- question and decision the measurement should support
- affected routes, templates, markets, devices, and query groups
- baseline period and comparison period
- primary metric and guardrail metrics
- known seasonality, campaigns, outages, releases, and tracking changes
- owner and review date

Do not present ranking, impressions, clicks, conversions, or answer-engine mentions as interchangeable outcomes.

## Launch And Migration Baseline
Capture before release:

- indexed and submitted URL counts
- representative URL Inspection results
- query/page/country/device performance
- top landing pages and conversion paths
- crawl errors, canonical selections, structured-data issues, and server errors
- redirect inventory and high-value old URLs
- release annotation and rollback threshold

After release, compare the same segments. Separate expected URL consolidation from accidental loss.

## Diagnosis Order
When traffic changes, check in this order:

1. analytics or consent instrumentation changes
2. outages, status codes, robots, noindex, canonicals, redirects, and rendering
3. release and template changes
4. indexing and crawl evidence
5. query, page, market, device, and feature segmentation
6. seasonality, demand, competition, and confirmed search-system updates

Do not attribute a change to an algorithm update merely because dates overlap.

## Generative Search Measurement
- Use platform-native reporting when available and state when AI-feature traffic is blended into broader search reporting.
- Track downstream quality such as engaged sessions, qualified leads, revenue, or task completion; mentions alone are weak evidence.
- Record prompt/query sets, geography, account state, model/platform, and observation date for manual answer-surface sampling.
- Treat small manual samples as directional, not statistically representative.

## Output
Report:

```markdown
Decision:
Baseline:
Change:
Observed effect:
Confidence and confounders:
Guardrail result:
Next measurement date:
```
