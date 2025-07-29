class SubnetInfoRuntimeApi:
    def __init__(self, substrate):
        self.substrate = substrate

    async def get_subnet_hyperparams(self, subnet):
        return {
            "activity_cutoff": 5000,
            "adjustment_alpha": 0,
            "adjustment_interval": 100,
            "alpha_high": 58982,
            "alpha_low": 45875,
            "bonds_moving_avg": 900000,
            "commit_reveal_period": 1,
            "commit_reveal_weights_enabled": False,
            "difficulty": 10000000,
            "immunity_period": 4096,
            "kappa": 32767,
            "liquid_alpha_enabled": False,
            "max_burn": 100000000000,
            "max_difficulty": 4611686018427387903,
            "max_regs_per_block": 1,
            "max_validators": 64,
            "max_weights_limit": 65535,
            "min_allowed_weights": 0,
            "min_burn": 500000,
            "min_difficulty": 10000000,
            "registration_allowed": True,
            "rho": 10,
            "serving_rate_limit": 50,
            "target_regs_per_interval": 2,
            "tempo": 100,
            "weights_rate_limit": 100,
            "weights_version": 0,
        }
