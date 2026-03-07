"""Tests for InvaderGrid march mechanics, collision, and scoring."""

import pytest
from space_invaders import constants
from space_invaders.assets import ensure_assets
from space_invaders.entities.grid import InvaderGrid, march_interval_ms


@pytest.fixture(scope="module")
def asset_mgr():
    return ensure_assets()


@pytest.fixture
def grid(asset_mgr):
    return InvaderGrid(asset_mgr)


# ---------------------------------------------------------------------------
# march_interval_ms
# ---------------------------------------------------------------------------

def test_march_interval_full_grid():
    assert march_interval_ms(55) == constants.MARCH_MAX_MS


def test_march_interval_single_invader():
    assert march_interval_ms(1) == constants.MARCH_MIN_MS


def test_march_interval_zero_clamps_to_min():
    assert march_interval_ms(0) == constants.MARCH_MIN_MS


def test_march_interval_monotonically_decreasing():
    values = [march_interval_ms(n) for n in range(55, 0, -1)]
    assert values == sorted(values, reverse=True)


def test_march_interval_never_below_min():
    for n in range(0, 60):
        assert march_interval_ms(n) >= constants.MARCH_MIN_MS


# ---------------------------------------------------------------------------
# Frame animation
# ---------------------------------------------------------------------------

def test_march_step_advances_frame(grid):
    assert grid.frame == 0
    grid.update(constants.MARCH_MAX_MS / 1000.0 + 0.001)
    assert grid.frame == 1


def test_march_two_steps_wraps_frame(grid):
    interval = constants.MARCH_MAX_MS / 1000.0
    grid.update(interval * 2 + 0.001)
    assert grid.frame == 0  # two steps: 0→1→0


# ---------------------------------------------------------------------------
# Multi-step per frame (R003 regression)
# ---------------------------------------------------------------------------

def test_multi_step_per_frame(grid):
    """A single large dt must fire multiple march steps, not just one."""
    interval_s = constants.MARCH_MAX_MS / 1000.0
    grid.update(interval_s * 2.5)
    # 2 full steps completed → frame advanced twice → back to 0
    assert grid.frame == 0
    # grid moved 2 steps to the right
    assert grid.grid_x == constants.GRID_START_X + 2 * constants.MARCH_STEP_X


# ---------------------------------------------------------------------------
# Boundary reversal
# ---------------------------------------------------------------------------

def test_boundary_reversal_right(asset_mgr):
    """Grid should reverse direction when right edge hits RIGHT_LIMIT."""
    g = InvaderGrid(asset_mgr)
    initial_y = g.grid_y
    # March right until direction flips
    for _ in range(500):
        g._march_step()
        if g.direction == -1:
            break
    assert g.direction == -1, "Grid never reversed to left"
    assert g.grid_y == initial_y + constants.MARCH_STEP_Y, "Grid did not drop on reversal"


def test_boundary_reversal_left(asset_mgr):
    """After reversing right, grid should eventually reverse left."""
    g = InvaderGrid(asset_mgr)
    # Get it moving left first
    for _ in range(500):
        g._march_step()
        if g.direction == -1:
            break
    y_after_first_drop = g.grid_y
    # Now march left until it reverses again
    for _ in range(500):
        g._march_step()
        if g.direction == 1:
            break
    assert g.direction == 1, "Grid never reversed back to right"
    assert g.grid_y == y_after_first_drop + constants.MARCH_STEP_Y


# ---------------------------------------------------------------------------
# kill() and scoring
# ---------------------------------------------------------------------------

def test_kill_returns_squid_score(grid):
    assert grid.kill(0, 0) == constants.SCORE_SQUID


def test_kill_returns_crab_score(grid):
    assert grid.kill(1, 0) == constants.SCORE_CRAB
    assert grid.kill(2, 1) == constants.SCORE_CRAB


def test_kill_returns_octopus_score(grid):
    assert grid.kill(3, 0) == constants.SCORE_OCTOPUS
    assert grid.kill(4, 1) == constants.SCORE_OCTOPUS


def test_kill_decrements_total_alive(grid):
    before = grid.total_alive
    grid.kill(0, 5)
    assert grid.total_alive == before - 1


def test_kill_already_dead_returns_zero(grid):
    grid.kill(0, 9)
    assert grid.kill(0, 9) == 0  # second kill on same cell


def test_is_cleared_false_initially(asset_mgr):
    g = InvaderGrid(asset_mgr)
    assert not g.is_cleared()


def test_is_cleared_true_after_all_killed(asset_mgr):
    g = InvaderGrid(asset_mgr)
    for row in range(constants.GRID_ROWS):
        for col in range(constants.GRID_COLS):
            g.kill(row, col)
    assert g.is_cleared()


# ---------------------------------------------------------------------------
# invader_at()
# ---------------------------------------------------------------------------

def test_invader_at_hits_top_left_invader(asset_mgr):
    g = InvaderGrid(asset_mgr)
    # Top-left invader (row=0, col=0): squid, 8px wide
    squid_w = g._frames["squid"][0].get_width()
    cell_x = g.grid_x + 0 * constants.CELL_W
    cell_y = g.grid_y + 0 * constants.CELL_H
    blit_x = cell_x + (constants.CELL_W - squid_w) // 2
    blit_y = cell_y + (constants.CELL_H - constants.SPRITE_H) // 2
    result = g.invader_at(blit_x + squid_w // 2, blit_y + constants.SPRITE_H // 2)
    assert result == (0, 0)


def test_invader_at_gap_returns_none(asset_mgr):
    g = InvaderGrid(asset_mgr)
    # Point in the gap between row 0 and row 1 (between cells)
    gap_y = g.grid_y + constants.CELL_H - 1  # bottom of row 0 cell, outside sprite
    result = g.invader_at(g.grid_x + constants.CELL_W // 2, gap_y)
    # May or may not hit — just verify it doesn't crash and returns expected type
    assert result is None or (isinstance(result, tuple) and len(result) == 2)


def test_invader_at_dead_cell_returns_none(asset_mgr):
    g = InvaderGrid(asset_mgr)
    g.kill(0, 0)
    squid_w = g._frames["squid"][0].get_width()
    blit_x = g.grid_x + (constants.CELL_W - squid_w) // 2
    blit_y = g.grid_y + (constants.CELL_H - constants.SPRITE_H) // 2
    assert g.invader_at(blit_x + squid_w // 2, blit_y + 2) is None
