package cmd

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/olekukonko/tablewriter"
	"github.com/spf13/cobra"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var planFilePath string

// outputFormat string

var planCostCmd = &cobra.Command{
	Use:   "plan-cost",
	Short: "Get plan cost",
	Long:  `Fetches cost based on plan.`,
	Run: func(cmd *cobra.Command, args []string) {
		if planFilePath == "" {
			fmt.Printf("The values for planFilePath can't be empty")
			return
		}
		fmt.Printf("Calculating plan cost using plan file: %s \n", planFilePath)
		ResourceParser(planFilePath, "rte")
	},
}

var infraCostCmd = &cobra.Command{
	Use:   "infra-cost",
	Short: "Get Total infra cost",
	Long:  "Get Total infra cost present in the terraform code",
	Run: func(cmd *cobra.Command, args []string) {
	},
}

var getCmd = &cobra.Command{
	Use:   "get",
	Short: "Get information",
	Long:  `Retrieve different cost-related data.`,
}

func init() {
	getCmd.AddCommand(planCostCmd)
	getCmd.AddCommand(infraCostCmd)

	planCostCmd.Flags().StringVarP(&planFilePath, "planpath", "p", "", "The path to the terraform json plan file")
}

func ResourceParser(filepath string, db string) {
	if _, err := os.Stat(filepath); os.IsNotExist(err) {
		fmt.Println("The specified file doesnt exist")
	}
	if !strings.HasSuffix(filepath, ".json") {
		fmt.Println("Please enter terraform plan file in json format")
	}

	data, err := os.ReadFile(filepath)
	if err != nil {
		fmt.Println("Error reading file:", err)
		return
	}

	var plan PartialPlan
	if err := json.Unmarshal(data, &plan); err != nil {
		fmt.Println("Error parsing JSON:", err)
		return
	}
	table := tablewriter.NewWriter(os.Stdout)
	table.Header([]string{"Name", "Resource Type", "Instance Type", "Region", "Monthly Cost (USD)"})
	for _, res := range plan.PlannedValues.RootModule.Resources {
		name_output := fmt.Sprintf("%v", res.Values["tags"].(map[string]interface{})["Name"])
		instanceType_output := fmt.Sprintf("%v", res.Values["instance_type"])
		region_output := fmt.Sprintf("%v", res.Values["region"])
		serviceCode_output := res.Type

		db, err := gorm.Open(sqlite.Open("pricing.db"), &gorm.Config{})
		if err != nil {
			log.Fatal("Failed to connect to database:", err)
		}
		usagetype := res.Values["instance_type"]

		serviceCode := resources[res.Type]
		fmt.Println(serviceCode)

		region := res.Values["region"]
		query := fmt.Sprintf("select priceperUnitUSD from pricing_flat where usagetype like '%%%s%%' and service_code like '%%%s%%' and regionCode like '%%%s%%'",
			usagetype, serviceCode, region)

		var strValue string
		result := db.Raw(query).Scan(&strValue)
		if result.Error != nil {
			log.Fatal("Query execution failed:", result.Error)
		}
		table.Append([]string{name_output, serviceCode_output, instanceType_output, region_output, strValue})

	}
	table.Render()
}
