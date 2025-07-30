import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen, cg_method

@dataclass
class HyperLogLogGen(BaseGen):
    max_subelements: int = 10
    
    @cg_method(cmd_type="hyperloglog", can_create_key=True)
    def pfadd(self, pipe: redis.client.Pipeline, key: str) -> None:
        elements = [self._rand_str(self.def_key_size) for _ in range(random.randint(1, self.max_subelements))]
        pipe.pfadd(key, *elements)
    
    @cg_method(cmd_type="hyperloglog", can_create_key=False)
    def pfmerge(self, pipe: redis.client.Pipeline, key: str) -> None:
        source_keys = [self._rand_key() for _ in range(random.randint(1, self.max_subelements))]
        pipe.pfmerge(key, *source_keys)

if __name__ == "__main__":
    hyper_log_log_gen = parse(HyperLogLogGen)
    hyper_log_log_gen.distributions = '{"pfadd": 100, "pfmerge": 100}'
    hyper_log_log_gen._run()
