-- Solarized colorscheme for AstroVim
-- Configured to work like spf13-vim solarized

return {
  -- Add solarized colorscheme
  {
    "maxmx03/solarized.nvim",
    lazy = false,
    priority = 1000,
    opts = {
      variant = "winter", -- winter, spring, summer, autumn
      transparent = {
        enabled = false,
      },
    },
  },
  -- Configure AstroUI to use solarized
  {
    "AstroNvim/astroui",
    opts = {
      colorscheme = "solarized",
    },
  },
}