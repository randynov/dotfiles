-- Alternative colorscheme options if solarized has issues
-- Choose one by renaming this file to colorscheme.lua

return {
  -- Option 1: Classic vim-colors-solarized (most compatible with spf13-vim)
  -- {
  --   "altercation/vim-colors-solarized",
  --   lazy = false,
  --   priority = 1000,
  --   config = function()
  --     vim.g.solarized_termcolors = 256
  --     vim.g.solarized_termtrans = 1
  --     vim.g.solarized_contrast = "normal"
  --     vim.g.solarized_visibility = "normal"
  --     vim.cmd.colorscheme("solarized")
  --   end,
  -- },

  -- Option 2: Use AstroVim's default dark theme (safest option)
  {
    "AstroNvim/astroui",
    opts = {
      colorscheme = "astrodark", -- or "astrolight"
    },
  },

  -- Option 3: Catppuccin (modern, solarized-like colors)
  -- {
  --   "catppuccin/nvim",
  --   name = "catppuccin",
  --   lazy = false,
  --   priority = 1000,
  --   opts = {
  --     flavour = "mocha", -- latte, frappe, macchiato, mocha
  --     background = {
  --       light = "latte",
  --       dark = "mocha",
  --     },
  --   },
  -- },
  -- {
  --   "AstroNvim/astroui",
  --   opts = {
  --     colorscheme = "catppuccin",
  --   },
  -- },
}