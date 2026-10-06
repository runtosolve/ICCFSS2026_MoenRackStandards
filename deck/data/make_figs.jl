# Generate the strength-curve and timeline figures for the deck.
#     julia data/make_figs.jl
# Uses CairoMakie in a throwaway environment. Palette from template.pptx: navy 0E2841, blue 156082, orange E97132.

import Pkg
Pkg.activate(; temp = true)
Pkg.add("CairoMakie"; io = devnull)
using CairoMakie

const NAVY = colorant"#0E2841"; const BLUE = colorant"#156082"; const ORANGE = colorant"#E97132"; const MUTED = colorant"#4B5666"
const OUT = @__DIR__
set_theme!(Theme(fontsize = 22, Axis = (xgridvisible = false, ygridvisible = false, spinewidth = 1.2,
                                        rightspinevisible = false, topspinevisible = false)))

# global (column) curve, AISI S100 / MH16.1 Eqs. 8.2-3, 8.2-4, as a fraction of Py
pne(λc) = λc <= 1.5 ? 0.658^(λc^2) : 0.877 / λc^2
# MH16.1-2021/2023 Eq. 8.2-6, Pnlg/Py
pnlg(λc, Q) = Q >= 1 ? pne(λc) : pne(λc) * (1 - (1 - Q) * pne(λc)^(Q / (1 - Q)))
# MH16.1-2012 Section 4.1.3.1, Ae Fn / (Fy Anetmin)
p2012(λc, Q) = pne(λc) * (1 - (1 - Q) * pne(λc)^Q)
# MH16.1 Eqs. 8.2-7, 8.2-8, distortional anchored at Pne (as a fraction of Py, given Pcrd/Py)
function pnld(λc, rd)
    Pne = pne(λc); λd = sqrt(Pne / rd)
    λd <= 0.561 ? Pne : (1 - 0.25 * (rd / Pne)^0.6) * (rd / Pne)^0.6 * Pne
end
# AISI S100 E4, distortional anchored at Py
function pnd_s100(rd)
    λd = sqrt(1 / rd)
    λd <= 0.561 ? 1.0 : (1 - 0.25 * rd^0.6) * rd^0.6
end

λ = range(0.0, 2.5; length = 400)

# ── local + global: 2012 effective area vs 2021 Pnlg ──
fig = Figure(size = (1100, 650))
ax = Axis(fig[1, 1]; xlabel = "global slenderness λc = √(Py / Pcre)", ylabel = "P / Py",
          title = "Local–global interaction with the stub-column Q factor", titlealign = :left)
lines!(ax, λ, pne.(λ); color = MUTED, linewidth = 2, label = "Pne (Q = 1)")
for (Q, c) in ((0.8, BLUE), (0.6, ORANGE))
    lines!(ax, λ, pnlg.(λ, Q); color = c, linewidth = 3.5, label = "MH16.1-2021/2023, Q = $Q")
    lines!(ax, λ, p2012.(λ, Q); color = c, linewidth = 2.5, linestyle = :dash, label = "MH16.1-2012, Q = $Q")
end
ylims!(ax, 0, 1.05); xlims!(ax, 0, 2.5)
axislegend(ax; position = :rt, framevisible = false, labelsize = 19)
save(joinpath(OUT, "fig_local_global.png"), fig; px_per_unit = 2)

# ── distortional: MH16.1 (anchored at Pne) vs S100 (anchored at Py), Pcrd/Py = 0.6 ──
fig = Figure(size = (1100, 650))
ax = Axis(fig[1, 1]; xlabel = "global slenderness λc = √(Py / Pcre)", ylabel = "P / Py",
          title = "Distortional strength for Pcrd = 0.6 Py", titlealign = :left)
rd = 0.6
lines!(ax, λ, pne.(λ); color = MUTED, linewidth = 2, label = "Pne, global")
lines!(ax, λ, min.(pne.(λ), pnd_s100(rd)); color = BLUE, linewidth = 3, linestyle = :dash,
       label = "min(Pne, Pnd), S100 anchored at Py")
lines!(ax, λ, pnld.(λ, rd); color = ORANGE, linewidth = 3.5, label = "Pnld, MH16.1 anchored at Pne")
ylims!(ax, 0, 1.05); xlims!(ax, 0, 2.5)
axislegend(ax; position = :rt, framevisible = false, labelsize = 19)
save(joinpath(OUT, "fig_dist_curve.png"), fig; px_per_unit = 2)

# ── edition timeline ──
fig = Figure(size = (1300, 230))
ax = Axis(fig[1, 1]; yticks = ([1], ["MH16.1"]), xticks = 2012:2:2024,
          leftspinevisible = false, bottomspinevisible = true, yticksvisible = false, xticklabelsize = 24, yticklabelsize = 28)
hidedecorations!(ax; ticklabels = false, ticks = false)
xlims!(ax, 2010, 2025); ylims!(ax, 0.75, 1.9)
for y in (1,); lines!(ax, [2010.3, 2024.7], [y, y]; color = (MUTED, 0.3), linewidth = 2); end
ev = [(2012, 1, "2012\neffective area, Q", MUTED), (2021, 1, "2021\nstrips, Q, and\nDSM distortional", ORANGE),
      (2023, 1, "2023\nASCE 7-22", BLUE)]
for (x, y, t, c) in ev
    scatter!(ax, [x], [y]; color = c, markersize = 24)
    ha = x == 2021 ? :right : x == 2023 ? :left : :center
    text!(ax, x + (ha == :right ? 0.3 : ha == :left ? -0.3 : 0), y + 0.14; text = t, align = (ha, :bottom), fontsize = 22, color = NAVY)
end
save(joinpath(OUT, "fig_timeline.png"), fig; px_per_unit = 2)
println("wrote fig_local_global.png, fig_dist_curve.png, fig_timeline.png to ", OUT)
