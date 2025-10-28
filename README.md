# Streaming Event demo: Coinbase → Redpanda Connect → Redpanda → Redis → Streamlit

This stack ingests live Coinbase ticker events over WebSocket into Redpanda using Redpanda Connect, sinks them to Redis, and visualizes them in a Streamlit app.

## Components
- **Redpanda**: Kafka-compatible streaming broker
- **Redpanda Connect (WebSocket)**: Ingests Coinbase WebSocket data into Redpanda topic
- **Redpanda Connect (Redis Sink)**: Streams data from Redpanda to Redis
- **Redis**: Target data store (database 1)
- **RedisInsight**: UI to inspect Redis data
- **Redpanda Console**: UI to inspect topics and messages
- **Streamlit**: Real-time dashboard for viewing ticker data

## Architecture Flow
```
Coinbase WebSocket → Redpanda Connect → coinbase_ticker topic → Redpanda Connect → Redis DB 1 → Streamlit
```

## Quick start

1. Start the stack
   ```bash
   docker compose up -d
   ```

2. Open the UIs
   - **Redpanda Console**: http://localhost:8080 (inspect topics and messages)
   - **RedisInsight**: http://localhost:5540 (visualize Redis data)
   - **Streamlit App**: http://localhost:8501 (live ticker dashboard)

3. Verify data flow
   - Check Redpanda Connect logs:
     ```bash
     docker logs -f redpanda-connect-ws
     docker logs -f redpanda-connect-redis
     ```
   - Inspect the `coinbase_ticker` topic in Redpanda Console
   - Messages should arrive within a few seconds from Coinbase

4. Connect to Redis in RedisInsight
   - Connection string: `redis://redis:6379/1`
   - Or manually:
     - Host: `redis`
     - Port: `6379`
     - Database Index: `1`

5. Inspect Redis from CLI
   - Check database size:
     ```bash
     docker exec redis redis-cli -n 1 DBSIZE
     ```
   - View keys:
     ```bash
     docker exec redis redis-cli -n 1 KEYS 'ticker:*' | head
     ```
   - Get a specific key:
     ```bash
     docker exec redis redis-cli -n 1 HGETALL ticker:BTC-USD:1234567890
     ```

## Configuration Files

- **connect-config.yaml**: Redpanda Connect WebSocket input configuration
- **redis-sink-config.yaml**: Redpanda Connect Redis output configuration
- **console-config.yml**: Redpanda Console UI configuration

## Notes and troubleshooting

- **Redpanda listeners**:
  - Internal listener for containers: `redpanda:9092`
  - External listener for host tools: `localhost:19092`
- **Redis database**: Data is stored in Redis database `1` (not default database `0`)
- **Redis key pattern**: `ticker:<product_id>:<timestamp>`
- If Coinbase WebSocket feed rate-limits or is temporarily unavailable, Redpanda Connect will retry automatically
- To change instruments, edit `connect-config.yaml` `open_message` to subscribe to different `product_ids` or channels (e.g., add "SOL-USD")

## Useful commands

- Follow logs:
  ```bash
  docker logs -f redpanda-connect-ws      # WebSocket ingestion
  docker logs -f redpanda-connect-redis   # Redis sink
  docker logs -f streamlit                # Streamlit app
  ```

- Consume from Redpanda topic (using rpk):
  ```bash
  docker exec redpanda rpk topic consume coinbase_ticker --num 10
  ```

- Consume from host (using kcat):
  ```bash
  kcat -b localhost:19092 -t coinbase_ticker -C -J -q | head -n 5
  ```

- Check Redpanda topic list:
  ```bash
  docker exec redpanda rpk topic list
  ```

## Customize

- **Change subscribed products**: Edit `connect-config.yaml` line 3 to add more product IDs
- **Change Redis key pattern**: Edit `redis-sink-config.yaml` line 13
- **Change Redis database**: Edit `redis-sink-config.yaml` line 17 and `streamlit_app.py` line 7
- **Adjust Streamlit refresh rate**: Use the sidebar slider in the Streamlit UI

## Tear down
```bash
docker compose down -v
```
