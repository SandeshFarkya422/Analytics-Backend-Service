"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("customer_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("customer_id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("idx_customers_email", "customers", ["email"])
    op.create_index("idx_customers_created_at", "customers", ["created_at"])

    op.create_table(
        "orders",
        sa.Column("order_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("order_date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("order_id"),
    )
    op.create_index("idx_orders_customer_id", "orders", ["customer_id"])
    op.create_index("idx_orders_order_date", "orders", ["order_date"])
    op.create_index("idx_orders_customer_date", "orders", ["customer_id", "order_date"])

    op.create_table(
        "refunds",
        sa.Column("refund_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("refund_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("refund_date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.order_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("refund_id"),
    )
    op.create_index("idx_refunds_order_id", "refunds", ["order_id"])
    op.create_index("idx_refunds_refund_date", "refunds", ["refund_date"])

    op.create_table(
        "analytics_summary",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("metric_value", sa.Numeric(20, 4), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("metric_name"),
    )

    op.create_table(
        "revenue_by_month",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("month", sa.String(7), nullable=False),
        sa.Column("revenue", sa.Numeric(20, 2), nullable=False),
        sa.Column("order_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("month"),
    )


def downgrade() -> None:
    op.drop_table("revenue_by_month")
    op.drop_table("analytics_summary")
    op.drop_table("refunds")
    op.drop_table("orders")
    op.drop_table("customers")
