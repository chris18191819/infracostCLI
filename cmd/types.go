package cmd

type Resource struct {
	Address      string                 `json:"address"`
	Mode         string                 `json:"mode"`
	Type         string                 `json:"type"`
	Name         string                 `json:"name"`
	ProviderName string                 `json:"provider_name"`
	Values       map[string]interface{} `json:"values"`
}

type RootModule struct {
	Resources []Resource `json:"resources"`
}

type PlannedValues struct {
	RootModule RootModule `json:"root_module"`
}

type PartialPlan struct {
	PlannedValues PlannedValues `json:"planned_values"`
}
