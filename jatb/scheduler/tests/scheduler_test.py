# Runs ExampleScheduler on real games. Start a race by hand in every game that pops up.
#   source utils/env.sh
#   poetry run python -m jatb.scheduler.tests.scheduler_test

from jatb.bot.policy import IPolicy
from jatb.scheduler import ExampleScheduler

NUM_PARALLEL = 2
NUM_POLICIES = 3
EPISODES_PER_POLICY = 2
EPISODE_MS = 5000

# ExampleScheduler doesn't call predict yet (the plugin doesn't accept actions)
class DummyPolicy(IPolicy):
    def predict(self, observation: list[float]) -> list[float]:
        return []

def main() -> None:
    scheduler = ExampleScheduler(NUM_PARALLEL, episodes_per_policy=EPISODES_PER_POLICY, episode_ms=EPISODE_MS)

    # close the games even on Ctrl+C or an error, otherwise TmForever processes are left behind
    try:
        results = scheduler.run_episodes([DummyPolicy() for _ in range(NUM_POLICIES)])
    finally:
        scheduler.close()

    for result in results:
        print(result)

    assert len(results) == NUM_POLICIES * EPISODES_PER_POLICY
    print(f"ok: {len(results)} episodes")

if __name__ == "__main__":
    main()