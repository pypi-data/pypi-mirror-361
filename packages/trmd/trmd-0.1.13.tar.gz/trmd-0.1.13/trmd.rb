class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/62/a7/c758ae7806172a6c0e707243eeb882ab6959276eb9a62320cd1609bf7970/trmd-0.1.12.tar.gz"
  sha256 "7f37fe5c57e37507ce7fab89fab98339a33819e03f13a268b71707d519efc8ea"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end
