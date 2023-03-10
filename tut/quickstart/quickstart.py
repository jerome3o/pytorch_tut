import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets
from torchvision.transforms import ToTensor

# Define model
class MyNeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28 * 28, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 10),
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits


def train(
    dataloader: DataLoader,
    model: MyNeuralNetwork,
    loss_fn,
    optimizer,
    device,
):
    size = len(dataloader.dataset)
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)

        # Compute prediction error
        pred = model(X)
        loss = loss_fn(pred, y)

        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(X)
            print(f"loss {loss:>7f} [{current:>5d}/{size:>5d}]")


def test(dataloader: DataLoader, model, loss_fn, device):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
        test_loss /= num_batches
        correct /= size
        print(
            f"Test Error: \n Accuracy: {100*correct:>0.1f}%, Avg loss = {test_loss:>8f} \n"
        )


def main():
    # Download training data from open datasets
    training_data = datasets.FashionMNIST(
        root="fashion_data",
        train=True,
        download=True,
        transform=ToTensor(),
    )

    # Download training data from open datasets
    test_data = datasets.FashionMNIST(
        root="fashion_data",
        train=False,
        download=True,
        transform=ToTensor(),
    )
    batch_size = 64

    # Create data loaders
    train_dataloader = DataLoader(training_data, batch_size=batch_size)
    test_dataloader = DataLoader(test_data, batch_size=batch_size)

    for X, y in test_dataloader:
        print(f"Shape of X [N, C, H, W]: {X.shape}")
        print(f"Shape of y: {y.shape} {y.dtype}")
        break

    # Get cpu or gpu device for training

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using {device} device")

    model = MyNeuralNetwork().to(device)

    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)

    epochs = 1
    for t in range(epochs):
        print(f"Epoch {t+1}\n-------------------------------")
        train(train_dataloader, model, loss_fn, optimizer, device)
        test(test_dataloader, model, loss_fn, device)
    print("Done!")

    model_path = "model.pth"
    torch.save(model.state_dict(), model_path)
    print(f"Saved PyTorch Model State to {model_path}")

    # loading model
    loaded_model = MyNeuralNetwork()
    loaded_model.load_state_dict(torch.load(model_path))

    print(loaded_model)

    classes = [
        "T-shirt/top",
        "Trouser",
        "Pullover",
        "Dress",
        "Coat",
        "Sandal",
        "Shirt",
        "Sneaker",
        "Bag",
        "Ankle boot",
    ]

    model.eval()
    x, y = test_data[0][0], test_data[0][1]

    with torch.no_grad():
        pred = loaded_model(x)
        predicted, actual = classes[pred[0].argmax(0)], classes[y]
        print(f"predicted: '{predicted}', Actual: '{actual}'")


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    main()
