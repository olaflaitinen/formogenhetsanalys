# Decomposition plots for wealth data
# Author: Förmögenhetsanalys
# Date: 2025-10-08

library(ggplot2)
library(readr)
library(tidyr)

# Load synthetic data
households <- read_parquet("data/synthetic/households.parquet")

# Reshape to long format
wealth_long <- households %>%
  select(household_id, financial_wealth, real_estate_wealth, business_wealth) %>%
  pivot_longer(
    cols = c(financial_wealth, real_estate_wealth, business_wealth),
    names_to = "component",
    values_to = "value"
  )

# Boxplot by component
ggplot(wealth_long, aes(x = component, y = value, fill = component)) +
  geom_boxplot() +
  scale_y_log10() +
  labs(title = "Wealth Distribution by Component", x = "Component", y = "Value (log scale)") +
  theme_minimal() +
  theme(legend.position = "none")

ggsave("figures/wealth_decomposition.png")
