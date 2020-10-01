all_agents_setting = {
    "resident_or_visitor": "any",
    "agent_age": ["0-6","7-17","18-35","36-60","61-100"],
    "modes": {
        "bicycle": True,
        "car": True,
        "foot": True,
        "public_transport": True
    }
}


def apply_time_filters(abm_result, time_filters):
    start_time = time_filters["start_time"]
    end_time = time_filters["end_time"]
    for agent_data in abm_result["data"]:
        agent_data["timestamps"] = list(filter(lambda x: start_time < x < end_time, agent_data["timestamps"]))
    abm_result["data"] = list(filter(lambda agent: agent["timestamps"], abm_result["data"]))


def apply_agent_filters(abm_result, agent_filters):
    if not agents_to_be_filtered(agent_filters):
        return abm_result

    relevant_agents_data = []
    for agent_data in abm_result["data"]:
        relevant_agent = True

        for key, value in agent_filters.items():
            try:
                if key == "modes":  # modes contains dict of allowed transport modes {"bicycle":true, "car":false}
                    if not value[agent_data["agent"]["mode"]]:
                        relevant_agent = False
                        break
                elif key == "agent_age":  # agent_age contains an array of allowed ages e.g. ['0-6', '18-35']
                    if not value[agent_data["agent"]["agent_age"]] in agent_filters["agent_age"]:
                        relevant_agent = False
                        break
                else:
                    if value == "any":  # any values for this key are excepted
                        continue
                    if not agent_data["agent"][key] in [value, "unknown"]:  # matching value or "unknown" is relevant
                        relevant_agent = False
                        break
            except Exception as e:
                print("filter criteria does not match target data")
                print(e)
                abort(400)
        if relevant_agent:
            relevant_agents_data.append(agent_data)

    abm_result["data"] = relevant_agents_data


def agents_to_be_filtered(agent_filters) -> bool:
    if agent_filters == all_agents_setting:
        return False

    return True

