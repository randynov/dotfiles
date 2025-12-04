-- Activated astrocore configuration for spf13-vim migration

-- AstroCore provides a central place to modify mappings, vim options, autocommands, and more!
-- Configuration documentation can be found with `:h astrocore`
-- NOTE: We highly recommend setting up the Lua Language Server (`:LspInstall lua_ls`)
--       as this provides autocomplete and documentation while editing

---@type LazySpec
return {
  "AstroNvim/astrocore",
  ---@type AstroCoreOpts
  opts = {
    -- Configure core features of AstroNvim
    features = {
      large_buf = { size = 1024 * 256, lines = 10000 }, -- set global limits for large files for disabling features like treesitter
      autopairs = true, -- enable autopairs at start
      cmp = true, -- enable completion at start
      diagnostics = { virtual_text = true, virtual_lines = false }, -- diagnostic settings on startup
      highlighturl = true, -- highlight URLs at start
      notifications = true, -- enable notifications at start
    },
    -- Diagnostics configuration (for vim.diagnostics.config({...})) when diagnostics are on
    diagnostics = {
      virtual_text = true,
      underline = true,
    },
    -- passed to `vim.filetype.add`
    filetypes = {
      -- see `:h vim.filetype.add` for usage
      extension = {
        foo = "fooscript",
      },
      filename = {
        [".foorc"] = "fooscript",
      },
      pattern = {
        [".*/etc/foo/.*"] = "fooscript",
      },
    },
    -- vim options configured to match spf13-vim settings
    options = {
      opt = { -- vim.opt.<key>
        -- Core display settings
        relativenumber = false, -- absolute line numbers like spf13
        number = true, -- sets vim.opt.number
        spell = true, -- enable spell checking like spf13
        signcolumn = "yes", -- sets vim.opt.signcolumn to yes
        wrap = true, -- enable line wrapping
        linebreak = true, -- break lines at word boundaries
        showbreak = "↪ ", -- show wrapped line indicator
        
        -- Indentation settings (matching spf13-vim)
        shiftwidth = 4, -- 4 space indentation
        tabstop = 4, -- tab width of 4
        softtabstop = 4, -- backspace deletes 4 spaces
        expandtab = true, -- tabs are spaces
        autoindent = true, -- indent at same level as previous line
        
        -- Search settings (matching spf13-vim)
        hlsearch = true, -- highlight search terms
        incsearch = true, -- find as you type search
        ignorecase = true, -- case insensitive search
        smartcase = true, -- case sensitive when uppercase present
        
        -- General settings
        mouse = "a", -- enable mouse usage
        clipboard = "unnamed", -- use system clipboard
        hidden = true, -- allow buffer switching without saving
        history = 1000, -- store more history
        backup = true, -- enable backups
        undofile = true, -- persistent undo
        cursorline = true, -- highlight current line
        showmatch = true, -- show matching brackets
        foldenable = true, -- enable folding
        scrolloff = 3, -- minimum lines above/below cursor
        
        -- Display settings
        list = true, -- show invisible characters
        listchars = { tab = "> ", trail = ".", extends = "#", nbsp = "_" },
        virtualedit = "onemore", -- allow cursor beyond last character
        
        -- Background
        background = "dark", -- dark background like spf13
      },
      g = { -- vim.g.<key>
        -- configure global vim variables (vim.g)
        -- NOTE: `mapleader` and `maplocalleader` must be set in the AstroNvim opts or before `lazy.setup`
        -- This can be found in the `lua/lazy_setup.lua` file
      },
    },
    -- Mappings can be configured through AstroCore as well.
    -- NOTE: keycodes follow the casing in the vimdocs. For example, `<Leader>` must be capitalized
    mappings = {
      -- first key is the mode
      n = {
        -- second key is the lefthand side of the map

        -- navigate buffer tabs
        ["]b"] = { function() require("astrocore.buffer").nav(vim.v.count1) end, desc = "Next buffer" },
        ["[b"] = { function() require("astrocore.buffer").nav(-vim.v.count1) end, desc = "Previous buffer" },

        -- spf13-vim inspired mappings
        ["<Leader>bd"] = {
          function()
            require("astroui.status.heirline").buffer_picker(
              function(bufnr) require("astrocore.buffer").close(bufnr) end
            )
          end,
          desc = "Close buffer from tabline",
        },
        
        -- Window navigation (spf13-vim style)
        ["<C-h>"] = { "<C-w>h", desc = "Move to left window" },
        ["<C-j>"] = { "<C-w>j", desc = "Move to bottom window" },
        ["<C-k>"] = { "<C-w>k", desc = "Move to top window" },
        ["<C-l>"] = { "<C-w>l", desc = "Move to right window" },
        
        -- Folding shortcuts (spf13-vim style)
        ["<Leader>f0"] = { ":set foldlevel=0<CR>", desc = "Fold level 0" },
        ["<Leader>f1"] = { ":set foldlevel=1<CR>", desc = "Fold level 1" },
        ["<Leader>f2"] = { ":set foldlevel=2<CR>", desc = "Fold level 2" },
        ["<Leader>f3"] = { ":set foldlevel=3<CR>", desc = "Fold level 3" },
        ["<Leader>f4"] = { ":set foldlevel=4<CR>", desc = "Fold level 4" },
        ["<Leader>f5"] = { ":set foldlevel=5<CR>", desc = "Fold level 5" },
        ["<Leader>f6"] = { ":set foldlevel=6<CR>", desc = "Fold level 6" },
        ["<Leader>f7"] = { ":set foldlevel=7<CR>", desc = "Fold level 7" },
        ["<Leader>f8"] = { ":set foldlevel=8<CR>", desc = "Fold level 8" },
        ["<Leader>f9"] = { ":set foldlevel=9<CR>", desc = "Fold level 9" },
        
        -- Background toggle (spf13-vim style)
        ["<Leader>bg"] = {
          function()
            if vim.o.background == "dark" then
              vim.o.background = "light"
            else
              vim.o.background = "dark"
            end
          end,
          desc = "Toggle background"
        },
        
        -- Search highlight toggle  
        ["<Leader>/"] = { ":set invhlsearch<CR>", desc = "Toggle search highlight" },
        
        -- Yank to end of line (spf13-vim style)
        ["Y"] = { "y$", desc = "Yank to end of line" },

        -- tables with just a `desc` key will be registered with which-key if it's installed
        -- this is useful for naming menus
        -- ["<Leader>b"] = { desc = "Buffers" },

        -- setting a mapping to false will disable it
        -- ["<C-S>"] = false,
      },
    },
  },
}
