# Authoritative Silicon Command/Reply Checklist

Use for cadence or any K1 silicon test requiring command/reply.

- [ ] Serial Studio is not the transport.
- [ ] Serial Studio has released target CDC.
- [ ] No autoReconnect process can steal the port.
- [ ] Target identity established by device evidence.
- [ ] pyserial/test harness has exclusive ownership.
- [ ] Device clock/counter is timing authority.
- [ ] Host timestamp is diagnostic only.
- [ ] Named test/GO exists if required by project governance.
- [ ] One proof obligation.
- [ ] No hidden retry.
- [ ] Result written before any unrelated restore/cleanup that could destroy evidence.
- [ ] Product restore, when applicable, happens after evidence exists.
- [ ] Receipt explicitly records port ownership and Serial Studio absence/release.
