# Engineering notes

How the system stays correct on store power, store networks and unattended servers. Each note gives the capability, how it works, and the test or check that guards it.

[Devices](#devices) · [Server and data](#server-and-data) · [Releases and operations](#releases-and-operations)

## Devices

### Power-loss-safe device state

Players raise and clear each problem once, and their problem state is written atomically. When the state is missing or unreadable after a boot, the first success of each check reports that problem cleared once, and the server ignores clears for problems it does not hold. No warning stays stuck after a power cut.

*Guard:* player tests for state lost across restarts and for whole-file saves.

### Duplicate device-credential detection

The server keeps the last address of each authenticated device in memory and flags a credential whose address switches four or more times within ten minutes as a likely duplicate device in the panel, with both addresses, and in the fleet report. One address change is a DHCP lease; alternation suggests two devices. Detection needs no per-request database write.

*Guard:* server device-watch tests.

### Silent-branch detection

Publishing proves nothing about what a store played. Players upload playback evidence in batches from a saved offset, the server deduplicates retries by fingerprint, and a permanently rejected batch cannot block later ones. Announcements that expire without a played report are counted per branch, with the player's reason or a missing-report flag, and shown first in the campaign summary.

*Guard:* device-events, uploader and playback-evidence tests; an end-to-end rehearsal on a Windows server, SQL Server and a Pi 4.

### Server-trusted clock

A Raspberry Pi has no battery-backed clock, and a VPN-only branch network may have no internet time. When network time is unavailable, the updater reads the server's time over the already-verified TLS connection, sets the clock if it is more than 2 seconds off, and the player trusts it for 24 hours of that boot; a Pi loses time only at reboot. Until then, music plays and announcements wait.

*Guard:* updater tests and shared sound-policy cases for an untrusted clock.

### At-most-once playback across crashes

Each announcement is claimed on disk before the music ducks. After a restart, an unfinished claim is dropped and reported. A hung announcement player is stopped after 300 seconds and recorded.

*Guard:* tests fail if the claim write or either hash check is removed; a SIGKILL during playback on a physical Pi produced exactly one dropped event and no replay.

### Offline prayer silence

Pis read hash-addressed quiet calendars for their district, fade music out and in, and drop an interrupted announcement rather than replay it. Silence covers both dawn-call times, and new districts get calendars soon after assignment.

*Guard:* one shared file of boundary cases (overnight, daylight saving, interval edges) runs on both device and server; a rehearsed prayer interval silenced a physical Pi on time and resumed.

### Audio proven on hardware

Speech and music target −16 LUFS with a −1.5 dBTP ceiling, and speech is re-measured before it is published. I traced silent audio on Raspberry Pi 3B+ hardware, with no error reported, to an ALSA `dmix` stage that opened its output but never advanced it; both players now open the card through `plug`.

*Guard:* normalizer tests, an ALSA configuration test, and an acceptance check by ear on the physical Pi.

## Server and data

### Race-proven publication

The scheduler queues up to twelve announcements per plan revision, never overlapping and expiring before prices go stale or the store closes. Publication locks plan rows in branch order.

*Guard:* PostgreSQL-only race tests: racing snapshots create exactly one campaign and one occurrence.

### Concurrency in the broker

I traced a shutdown deadlock inside the third-party MQTT library to a recursive read lock and fixed it locally, without forking the library.

*Guard:* 200 repeated race-detector runs of the broker package.

### Restores that keep device trust

Pis trust the server's internal certificate authority, so backups carry it and a server restored at the same address keeps every device's trust. Nightly off-site copies are sealed with AES-256-GCM keys wrapped by the owner's RSA key, so the relay cannot read them. Retention pruning locks rows and deletes objects first, so concurrent writers never lose audio.

*Guard:* a restore rehearsal from an off-site copy matched every table row for row; retention race tests.

### Safe ERP connection changes

A new ERP connection waits as a candidate with a sealed password and replaces the working one only after the collector's test passes. Failures reach the panel as plain Turkish reasons.

*Guard:* source-sync tests, verified against SQL Server 2022.

## Releases and operations

### Clean-Windows release pipeline

Every installer that may reach a customer runs through a GitHub Actions matrix on clean Windows runners: a fresh install under Turkish regional settings, an upgrade from each maintained customer release, and updates forced to roll back with and without a database restore, linted, with StrictMode checks under PowerShell 5.1 and 7. Building both test installers from one payload in parallel halved the build time.

*Guard:* the workflow itself; by default, publishing signs the exact installer that was tested.

### Transactional upgrades with a reported outcome

A failed service changeover restores the previous release and, if the backup finished, its database. The outcome, failing step and reason reach the fleet hub, and the customer sees one plain sentence that asks for action only when they can fix it.

*Guard:* installer rollback scenarios in the clean-runner matrix.

### Pi updates with automatic rollback

A systemd timer pulls the player matching its server's release, downloads only when the code changed, builds it beside the running one and switches by directory rename. If the service is not healthy after 90 seconds, it switches back.

*Guard:* a deliberately crashing package rolled back at the 90-second check, its failure visible in the panel.

### Validated on real Windows 11

I hardened the Linux-first stack on real Windows 11 for what emulation hides: byte order marks Go rejects, PowerShell 5.1 quoting, `initdb` permissions and IP-only clients without SNI.

*Guard:* silent and wizard installs, rerun, update with backup, address change and rollback, all on real Windows 11.

### Outbound-only monitoring

Customer servers publish retained state, events and install outcomes over MQTT 5 with Last Will presence. A Go hub with per-customer ACLs exposes Prometheus metrics, and dashboards and Grafana alert rules are provisioned from the repository. A nightly support file with logs and Excel-ready reports reaches me without access to customer networks.

*Guard:* Go tests for hub auth, topic ACLs, event deduplication and uplink to hub end to end.
