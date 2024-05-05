from dataclasses import dataclass
from decimal import Decimal
from typing import Coroutine

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll, Center
from textual.events import Resize
from textual.widgets import (
    Button,
    Input,
    Static,
    Label,
    Placeholder,
    ContentSwitcher,
    Markdown,
)
from textual.reactive import reactive


ABOUT_MD = """
1. Amazing awesome coffee shop brought to you by @willmcgugan

2. Will's Coffee, Inc
"""


@dataclass
class Product:
    name: str
    sku: str
    price: Decimal
    description: str


PRODUCTS = [
    Product(
        name="nil blend coffee",
        sku="whole bean | medium roast | 12oz",
        price=Decimal("25"),
        description="Dive into the rich taste of Nil, our delicious semi-sweet coffee with notes of chocolate, peanut butter, and a hint of fig.",
    ),
    Product(
        name="None blend coffee",
        sku="whole bean | light roast | 500g",
        price=Decimal("19.95"),
        description="Delicious honey method coffee, with hints of caramel",
    ),
]


@dataclass
class Question:
    q: str
    a: str


FAQS = [
    Question("Where do you ship?", "We don't."),
    Question("Is your coffee ethically sourced?", "Yes."),
    Question("What is the meaning of life the universe and everything?", "42"),
]


class Column(Vertical):
    pass


class Footer(Horizontal):
    def compose(self) -> ComposeResult:
        yield Label("Footer goes here")


class Panel(Vertical):
    def __init__(self, label: str, id: str) -> None:
        self.label = label
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        yield VerticalScroll(classes="content")
        yield Footer()


class OrderCounter(Horizontal):
    order_count = reactive(0, recompose=True)

    def compose(self) -> ComposeResult:
        yield Label("-", classes="minus")
        yield Label(str(self.order_count), classes="count")
        yield Label("+", classes="plus")


class ProductWidget(Vertical, can_focus=True):
    order_count = reactive(0)

    BINDINGS = [
        ("minus", "order(-1)"),
        ("plus", "order(+1)"),
    ]

    def __init__(self, product: Product) -> None:
        self.product = product
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static(self.product.name, classes="name")
        yield Static(self.product.sku, classes="sku")
        yield Static(f"${self.product.price:.02f}", classes="price")
        yield Static(self.product.description, classes="description")
        yield OrderCounter().data_bind(ProductWidget.order_count)

    def action_order(self, delta: int) -> None:
        self.order_count = max(0, self.order_count + delta)


class ProductsPanel(Vertical):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            for product in PRODUCTS:
                yield ProductWidget(product)

        yield Label(
            "[b]+[/] add   [b]-[/] remove   [b]c[/] cart   [b]q[/] quit",
            classes="footer",
        )


class AboutPanel(Vertical):
    def compose(self) -> ComposeResult:
        with Vertical(classes="content"):
            yield Markdown(ABOUT_MD)
        yield Label("[b]c[/] cart", classes="footer")


class FAQPanel(Vertical):
    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="content"):
            for question in FAQS * 10:
                yield Label(question.q, classes="question")
                yield Label(question.a, classes="answer")

        yield Label(
            "[b]c[/] cart",
            classes="footer",
        )


class CartPanel(Vertical):
    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="content"):
            yield Label("name")
            yield Input("", placeholder="Your name")
            yield Label("Credit card")
            yield Input("", placeholder="XXXX-XXXX-XXXX-XXXX")
            yield Label("Address 1")
            yield Input()
            yield Label("Address 2")
            yield Input()
            yield Label("Zip / Postcode")
            yield Input()
            yield Button("Place order", variant="success")

        yield Label(
            "[b]tab[/] Next field   [b]shift+tab[/] Previous field",
            classes="footer",
        )


class Header(Container):
    active_panel = reactive("shop", recompose=True)

    def compose(self) -> ComposeResult:
        active_panel = self.active_panel
        yield Label("[b]Terminal")
        yield Label("[b]s[/b] Shop", classes="active" if active_panel == "shop" else "")
        yield Label(
            "[b]a[/b] About", classes="active" if active_panel == "about" else ""
        )
        yield Label("[b]f[/b] Faq", classes="active" if active_panel == "faq" else "")
        yield Label("[b]c[/b] Cart", classes="active" if active_panel == "cart" else "")


class CoffeeApp(App):
    CSS_PATH = "coffee.tcss"
    DEFAULT_CLASSES = "narrow"

    active_panel = reactive("shop")

    BINDINGS = [
        ("s", "switch_panel('shop')"),
        ("a", "switch_panel('about')"),
        ("f", "switch_panel('faq')"),
        ("c", "switch_panel('cart')"),
        ("q", "quit"),
    ]

    def compose(self) -> ComposeResult:
        with Column():
            yield Header().data_bind(CoffeeApp.active_panel)
            with ContentSwitcher(initial="shop"):
                yield ProductsPanel(id="shop")
                yield AboutPanel(id="about")
                yield FAQPanel(id="faq")
                yield CartPanel(id="cart")

    def action_switch_panel(self, panel: str) -> None:
        self.active_panel = panel
        self.query_one(ContentSwitcher).current = panel

    def on_resize(self, event: Resize) -> None:
        self.query_one("Screen").set_class(self.size.width < 60, "narrow")


if __name__ == "__main__":
    app = CoffeeApp()
    app.run()
