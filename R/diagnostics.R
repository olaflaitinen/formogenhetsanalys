# Diagnostic plots for wealth data
# Author: Förmögenhetsanalys
# Date: 2025-10-08

library(ggplot2)
library(readr)

# Load synthetic data
households <- read_parquet("data/synthetic/households.parquet")

# Lorenz curve
lorenz_curve <- function(data, var) {
  data <- data[order(data[[var]]), ]
  cum_wealth <- cumsum(data[[var]])
  cum_share <- cum_wealth / max(cum_wealth)
  cum_pop <- seq_along(data[[var]]) / length(data[[var]])
  data.frame(pop = cum_pop, wealth = cum_share)
}

lorenz <- lorenz_curve(households, "total_wealth")

ggplot(lorenz, aes(x = pop, y = wealth)) +
  geom_line() +
  geom_abline(intercept = 0, slope = 1, linetype = "dashed") +
  labs(title = "Lorenz Curve", x = "Cumulative population", y = "Cumulative wealth") +
  theme_minimal()

ggsave("figures/lorenz_curve.png")
