# Kadans

**In-store audio and AI announcements for a regional, multi-city grocery chain with more than 20 branches, live in its first branches and rolling out branch by branch. I designed, built and run it in production, end to end, as the sole engineer.**

Eligible discounts in the customer's ERP become short Turkish announcements over the store's music. One HQ server on the customer's network plans promotions, music, opening hours and prayer silence per branch; Raspberry Pi players in the stores follow their cached plans through network outages. A language model chooses the words; every number comes from code.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/price-to-speaker-dark.svg">
  <img alt="Ten steps from a price change in the customer's ERP to an announcement in the store, with a chart of the music ducking under it" src="assets/price-to-speaker-light.svg">
</picture>

<sub>*Kadans* is Turkish for cadence; *Tellal* was the Ottoman town crier. The source code is private company property; screenshots and audio use test data.</sub>

## At a glance

| | |
|---|---|
| **Role** | Sole software engineer: architecture, build, deployment into the customer's systems, releases and operations |
| **Customer** | A regional, multi-city grocery chain with 20+ branches |
| **Runs on** | The customer's Windows server, Raspberry Pi players in the stores, and two cloud services I built: Tellal and a fleet hub |
| **Integrates with** | The customer's SQL Server ERP (read-only), branch network and VPN, and Windows server; Claude (Anthropic) and ElevenLabs through Tellal |
| **Delivery** | Under three months from first commit to first customer; two days later, after the office canary, its server [updated itself overnight and reported success](docs/milestones.md) |
| **Stack** | Python, FastAPI, PostgreSQL, Go, MQTT 5, React, TypeScript, Raspberry Pi, Linux, PowerShell, GitHub Actions, Prometheus, Grafana |

![Panel walkthrough: an ERP discount with its Turkish sentence and audio, then the music library with loudness states](assets/kadans-panel-flow.gif)

*The headquarters panel, shown with test fixtures: an ERP discount with the sentence the store will hear and its audio, then the music library, whose tracks reach the stores loudness-normalized.*

**Listen:** [MP3](assets/announcement-sample.mp3) · [video with the text](assets/announcement-sample.mp4). A sample in the production voice, generated from test data (8.9 s): *"Ayçiçek yağı 5 litre, 349 lira yerine 299 lira. Bu fırsat 20 Kasım tarihinde sizleri bekliyor."* (Sunflower oil, 5 litres: 299 lira instead of 349 lira. This offer awaits you on 20 November.)

## Architecture

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/architecture-dark.svg">
  <img alt="Architecture: ERP, headquarters panel, the Kadans server and branch Pi players inside the customer network; Tellal, the fleet hub and signed releases in the cloud" src="assets/architecture-light.svg">
</picture>

- **The server publishes state, never commands.** Each branch gets a versioned plan snapshot, and its player decides locally when an announcement may start, so music, hours and prayer silence carry on through network outages.
- **Two planes.** HTTPS is authoritative for plans, audio and proof of play. MQTT 5 carries revision hints, presence and live state; players also poll every 20 seconds, so a missing broker only slows delivery.
- **A store depends only on its own HQ server.** Speech generation, monitoring, support files, backups and updates reach the cloud through outbound connections from that server.

[Full architecture →](docs/architecture.md)

## Key decisions

| Chosen | Why | Rejected |
|---|---|---|
| Declarative, versioned plan snapshots with SHA-256-addressed audio | A lost or repeated message cannot misplay a store | Imperative play commands |
| At-most-once announcements, claimed on disk before the music ducks | A repeated promotion costs more than a missed one | At-least-once playback |
| The model writes words around placeholders; code inserts prices and dates | Removes the failure mode instead of checking for it | Checking numbers after generation |
| Budget new speech against the next 24 hours of branch opening time | Speech spend follows the airtime stores can actually play | Voicing every discount on arrival |
| Opaque device credentials, stored only as digests and issued to a chosen branch | Simple rotation and revocation, nothing to forge | JWTs; pairing through an unauthenticated endpoint |
| Outbound-only fleet reporting over MQTT on port 443 | Customer firewalls need nothing new | Inbound access or a remote VPN for operations |

Costs and rejected alternatives: [design decisions →](docs/decisions.md)

## Reliability: how it holds up

| When… | …the system |
|---|---|
| The network or the server is down | keeps playing from the last verified plan; hours, prayer silence and start windows still hold offline |
| Power drops mid-announcement or mid-write | drops that announcement instead of replaying it; device state is written atomically and heals itself |
| An announcement expires without proof of play | shows the player's reason in the panel, or flags the missing report |
| An ERP read fails | keeps offers without extending their start windows; only a successful read can withdraw them |
| One credential is used by two devices | flags the likely duplicate in the panel and the fleet report |
| A release is bad | stops at the office canary by default; a failed server changeover restores the previous release, and a Pi whose new player fails its 90-second health check switches back |
| The model writes a number | rejects the copy and asks for up to two rewrites; if none passes, the store hears the verified standard sentence in the same voice |
| The customer's disk is lost | restores at the same address from a nightly off-site backup sealed to the owner's key, and every player keeps trusting it |

[Engineering notes →](docs/engineering-notes.md)

## Built on Tellal

Copy and speech come from [Tellal](https://github.com/berkaybakac/tellal-case-study), the AI gateway I built alongside Kadans: Claude (Anthropic) writes words around placeholders, code inserts every price, ElevenLabs speaks the final text, and prepaid balances, scoped keys and spend limits guard every paid call. Kadans sends only verified facts and keeps a deterministic standard sentence for when no copy can be had. Tellal also serves signed releases and relays sealed backups; its panel shows the separate Kadans fleet hub.

## How I work

I own the architecture, every decision and every release, and write each decision down with its trade-off. I proved the core playback tests by removing each guarantee once and watching them fail. I use Claude Code and Codex daily as coding agents under test-enforced repository rules and per-step approval, and verify every change and review finding against the code myself.

## Read more

- [Architecture](docs/architecture.md): components, the two planes, trust boundaries and integration with the customer's systems.
- [Design decisions](docs/decisions.md): what was chosen, why, what it costs, and what was rejected.
- [Engineering notes](docs/engineering-notes.md): how the system stays correct on store power, store networks and unattended servers.
- [Tellal case study](https://github.com/berkaybakac/tellal-case-study): the AI gateway.
- [Milestones](docs/milestones.md): how it reached its first customer.

[AnnounceFlow](https://github.com/berkaybakac/announceflow) was the per-store predecessor: one installation per store, adopted by four customers at four locations. Kadans moves control to headquarters while each store still decides on its own what to play.

Other production work: [Turnstile](https://github.com/berkaybakac/turnstile-case-study) · [all projects](https://github.com/berkaybakac)
