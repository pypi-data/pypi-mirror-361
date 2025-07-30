r'''
# CDK Express Pipeline

[![npm version](https://badge.fury.io/js/cdk-express-pipeline.svg)](https://badge.fury.io/js/cdk-express-pipeline)
[![PyPI version](https://badge.fury.io/py/cdk-express-pipeline.svg)](https://badge.fury.io/py/cdk-express-pipeline)

<!-- TOC -->

* [Introduction](#introduction)
* [How does it work?](#how-does-it-work)
* [Deployment Order](#deployment-order)
* [Installation](#installation)
* [Usage](#usage)
* [Options](#options)
* [Selective Deployment](#selective-deployment)
* [Builds System Templates/Examples](#builds-system-templatesexamples)
* [GitHub CI Workflow Generation](#github-ci-workflow-generation)
* [Legacy Usage](#legacy-usage)
* [Demo Projects](#demo-projects)
* [Docs](#docs)

<!-- TOC -->

## Introduction

CDK Express Pipelines is a library that allows you to define your pipelines in CDK native method. It is built on
top of the [AWS CDK](https://aws.amazon.com/cdk/) and is an alternative
to [AWS CDK Pipelines](https://aws.amazon.com/cdk/pipelines/)
that is build system agnostic.

Features:

* Works on any system for example your local machine, GitHub, GitLab, etc.
* Uses the `cdk deploy` command to deploy your stacks
* It's fast. Make use of concurrent/parallel Stack deployments
* Stages and Waves are plain classes, not constructs, they do not change nested Construct IDs (like CDK Pipelines)
* Supports TS and Python CDK

Resources:

* [CDK Express Pipeline Tutorial](https://rehanvdm.com/blog/cdk-express-pipeline-tutorial)
* [Migrate from CDK Pipelines to CDK Express Pipeline](https://rehanvdm.com/blog/migrate-from-cdk-pipelines-to-cdk-express-pipeline)
* [Exploring CI/CD with AWS CDK Express Pipeline: Faster and Efficient Deployments](https://www.youtube.com/watch?v=pma4zP7mhMU)
  (YouTube channel [CI and CD on Amazon Web Services (AWS)](https://www.youtube.com/watch?v=pma4zP7mhMU))

## How does it work?

This library makes use of the fact that the CDK CLI computes the dependency graph of your stacks and deploys them in
the correct order. It creates the correct dependency graph between Waves, Stages and Stacks with the help of the
native `.addDependency` method of the CDK Stack. The `cdk deploy '**'` command will deploy all stacks in the correct
order.

## Installation

### TS

```bash
npm install cdk-express-pipeline
```

Then import the library in your code:

```python
import { CdkExpressPipeline } from 'cdk-express-pipeline';
```

### Python

```bash
pip install cdk-express-pipeline
```

Then import the library in your code:

```python
from cdk_express_pipelines import CdkExpressPipeline
```

## Usage

The `ExpressStack` extends the `cdk.Stack` class and has a very similar signature, only taking an extra `stage`
parameter. There are multiple ways to build your pipeline, it involves creating the Pipeline, adding Waves, Stages and
Stacks to your Stages and then calling `.synth()` on the Pipeline. See the alternative expand sections for other
methods.

**Stack Definition:**

```python
  class StackA extends ExpressStack {
  constructor(scope: Construct, id: string, stage: ExpressStage, stackProps?: StackProps) {
    super(scope, id, stage, stackProps);

    new cdk.aws_sns.Topic(this, 'MyTopic');
    // ... more resources
  }
}

class StackB extends ExpressStack {
  //... similar to StackA
}

class StackC extends ExpressStack {
  //... similar to StackA
}
```

**1️⃣ Pipeline Definition:**

```python
const app = new App();
const expressPipeline = new CdkExpressPipeline();

// === Wave 1 ===
const wave1 = expressPipeline.addWave('Wave1');
// --- Wave 1, Stage 1---
const wave1Stage1 = wave1.addStage('Stage1');

const stackA = new StackA(app, 'StackA', wave1Stage1);
const stackB = new StackB(app, 'StackB', wave1Stage1);
stackB.addExpressDependency(stackA);

// === Wave 2 ===
const wave2 = expressPipeline.addWave('Wave2');
// --- Wave 2, Stage 1---
const wave2Stage1 = wave2.addStage('Stage1');
new StackC(app, 'StackC', wave2Stage1);
expressPipeline.synth([
  wave1,
  wave2,
]);
```

The stack deployment order will be printed to the console when running `cdk` commands:

```plaintext
ORDER OF DEPLOYMENT
🌊 Waves  - Deployed sequentially.
🏗️ Stages - Deployed in parallel by default, unless the wave is marked `[Seq 🏗️]` for sequential stage execution.
📦 Stacks - Deployed after their dependent stacks within the stage (dependencies shown below them with ↳).
           - Lines prefixed with a pipe (|) indicate stacks matching the CDK pattern.
           - Stack deployment order within the stage is shown in square brackets (ex: [1])

🌊 Wave1
  🏗️ Stage1
    📦 StackA (Wave1_Stage1_StackA) [1]
    📦 StackB (Wave1_Stage1_StackB) [2]
        ↳ StackA
🌊 Wave2
  🏗️ Stage1
    📦 StackC (Wave2_Stage1_StackC) [1]
```

<br><details>
<summary><b>2️⃣ Pipeline Definition Alternative - Stacks Nested in Stages:</b></summary>

```python
const app = new App();

class Wave1 extends ExpressWave {
  constructor() {
    super('Wave1');
  }
}

class Wave1Stage1 extends ExpressStage {
  constructor(wave1: Wave1) {
    super('Stage1', wave1);

    const stackA = new StackA(app, 'StackA', this);
    const stackB = new StackB(app, 'StackB', this);
    stackB.addExpressDependency(stackA);
  }
}

class Wave2 extends ExpressWave {
  constructor() {
    super('Wave2');
  }
}

class Wave2Stage1 extends ExpressStage {
  constructor(wave2: Wave2) {
    super('Stage1', wave2);

    new StackC(app, 'StackC', this);
  }
}

const expressPipeline = new CdkExpressPipeline();
const wave1 = new Wave1();
new Wave1Stage1(wave1);
const wave2 = new Wave2();
new Wave2Stage1(wave2);
expressPipeline.synth([wave1, wave2]);
```

</details><br><details>
<summary><b>3️⃣ Pipeline Definition Alternative - Extending all without nesting:</b></summary>

```python
const app = new App();

// --- Custom Wave Class ---
class MyExpressWave extends ExpressWave {
  constructor(props: ExpressWaveProps) {
    super('My' + props.id);
  }
}

// --- Custom Stage Class ---
class MyExpressStage extends ExpressStage {
  constructor(id: string, wave: MyExpressWave, stacks?: MyExpressStack[]) {
    super('My' + id, wave, stacks);
  }
}

// --- Custom Stack Class ---
class MyExpressStack extends ExpressStack {
  constructor(scope: Construct, id: string, stage: MyExpressStage, stackProps?: StackProps) {
    super(scope, 'My' + id, stage, stackProps);
  }
}

const expressPipeline = new CdkExpressPipeline();
const wave1 = new MyExpressWave({ id: 'Wave1' });
const wave1Stage1 = new MyExpressStage('Stage1', wave1);
const stackA = new MyExpressStack(app, 'StackA', wave1Stage1);
expressPipeline.synth([wave1]);

expect(stackA.id).toBe('MyWave1_MyStage1_MyStackA');
```

</details>

## Deployment Order

The Wave, Stage and Stack order is as follows:

* Waves are deployed sequentially, one after the other.
* Stages within a Wave are deployed in parallel by default, unless configured to be sequential.
* Stacks within a Stage are deployed in order of stack dependencies within a Stage.

For example, the following definition of Waves, Stages and Stacks as in CDK Express Pipelines:

![order.png](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/_imgs/order-25smaller.png)

Will create a dependency graph as follows:

![img.png](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/_imgs/order_dependencies-25smaller.png)

When used with `cdk deploy '**' --concurrency 10`, it will deploy all stacks in parallel, 10 at a time, where possible
while still adhering to the dependency graph. Stacks will be deployed in the following order:

<details>
<summary>✨ Deployment order visualized ✨</summary>

![order_1.png](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/_imgs/order_1.png)

![order_2.png](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/_imgs/order_2.png)

![order_3.png](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/_imgs/order_3.png)

![order_4.png](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/_imgs/order_4.png)

![order_5.png](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/_imgs/order_5.png)

</details>

### Console Output

The Deployment Order can be printed to the console when running the `pipeline.synth` function, it is enabled by default
but can be disabled in the function arguments.

Let's use an example of a pipeline that features all possible display options:

<details>
<summary>Verbal explanation of the output</summary>

There are three waves. Waves run sequentially. Within each wave, stages run in parallel unless marked `[Seq 🏗]`,
which only Wave3 is. Stacks in a stage deploy in the order based on their dependencies, shown with arrows (`↳`),
and their position in the deployment order is indicated with square brackets like `[1]`.

Wave1 has two stages. In Stage1, StackA and StackF (shown by `[1]`) deploy first. StackB, StackC, and StackE (`[2]`)
follow, all depending on earlier stacks. StackD (`[3]`) is last, depending on StackB and StackF. Stage2 runs in
parallel and deploys StackA and StackB (`[1]`) first, followed by StackC (`[2]`), which depends on StackB.

Wave2 has two stages, all stacks (`[1]`) in both stages deploy at the same time since they have no dependencies.

Wave3 is marked `[Seq 🏗]`, so its stages run one after another. Stage1 deploys StackL and StackM (`[1]`) at the same
time, and then Stage3 deploys StackN and StackO (`[1]`).

The stack selector is shown in parentheses next to each stack. For example, Wave1 Stage1 StackA has the selector
`Wave1_Stage1_StackA`. Since every line begins with a pipe (`|`), we can infer that the command used was
`cdk (diff|deploy) '**'`, meaning all stacks are targeted with this command. We could instead have targeted a specific
wave, stage or stack by using a command like `cdk (diff|deploy) 'Wave1_Stage1_*'`, which would only deploy the stacks
in Wave1 Stage1.

</details>

```plaintext
ORDER OF DEPLOYMENT
🌊 Waves  - Deployed sequentially.
🏗 Stages - Deployed in parallel by default, unless the wave is marked `[Seq 🏗]` for sequential stage execution.
📦 Stacks - Deployed after their dependent stacks within the stage (dependencies shown below them with ↳).
           - Lines prefixed with a pipe (|) indicate stacks matching the CDK pattern.
           - Stack deployment order within the stage is shown in square brackets (ex: [1])

| 🌊 Wave1
|   🏗 Stage1
|     📦 StackA (Wave1_Stage1_StackA) [1]
|     📦 StackB (Wave1_Stage1_StackB) [2]
|        ↳ StackA
|     📦 StackC (Wave1_Stage1_StackC) [2]
|        ↳ StackA
|     📦 StackD (Wave1_Stage1_StackD) [3]
|        ↳ StackB, StackF
|     📦 StackE (Wave1_Stage1_StackE) [2]
|        ↳ StackF
|     📦 StackF (Wave1_Stage1_StackF) [1]
|   🏗 Stage2
|     📦 StackA (Wave1_Stage2_StackA) [1]
|     📦 StackB (Wave1_Stage2_StackB) [1]
|     📦 StackC (Wave1_Stage2_StackC) [2]
|        ↳ StackB
| 🌊 Wave2
|   🏗 Stage1
|     📦 StackH (Wave2_Stage1_StackH) [1]
|     📦 StackI (Wave2_Stage1_StackI) [1]
|   🏗 Stage2
|     📦 StackJ (Wave2_Stage2_StackJ) [1]
|     📦 StackK (Wave2_Stage2_StackK) [1]
| 🌊 Wave3 [Seq 🏗]
|   🏗 Stage1
|     📦 StackL (Wave3_Stage1_StackL) [1]
|     📦 StackM (Wave3_Stage1_StackM) [1]
|   🏗 Stage2
|     📦 StackN (Wave3_Stage2_StackN) [1]
|     📦 StackO (Wave3_Stage2_StackO) [1]
```

### Mermaid Graph File Output

The Deployment Order can also be outputted to a markdown file containing a Mermaid graph. This option is **disabled** by
default, and can be enabled when running the `pipeline.synth`. The output defaults to the root of the project with the
filename `pipeline-deployment-order.md`, this too can be changed in the function arguments.

Let's use, the same example as above, of a pipeline that features all possible display options:

<details>
<summary>Verbal explanation of the output</summary>

There are three waves. Waves run sequentially. Within each wave, stages run in parallel unless indicated by an arrow,
which only Wave3's stages are. Stacks in a stage deploy in the order based on their dependencies, shown with arrows,
and their position in the deployment order is indicated with square brackets like `[1]`.

Wave1 has two stages. In Stage1, StackA and StackF (shown by `[1]`) deploy first. StackB, StackC, and StackE (`[2]`)
follow, all depending on earlier stacks. StackD (`[3]`) is last, depending on StackB and StackF. Stage2 runs in
parallel and deploys StackA and StackB (`[1]`) first, followed by StackC (`[2]`), which depends on StackB.

Wave2 has two stages, all stacks (`[1]`) in both stages deploy at the same time since they have no dependencies.

Wave3 is marked `[Seq 🏗]`, so its stages run one after another. Stage1 deploys StackL and StackM (`[1]`) at the same
time, and then Stage3 deploys StackN and StackO (`[1]`).

The stack selector is shown in parentheses next to each stack. For example, Wave1 Stage1 StackA has the selector
`Wave1_Stage1_StackA`. Since every line begins with a pipe (`|`), we can infer that the command used was
`cdk (diff|deploy) '**'`, meaning all stacks are targeted with this command. We could instead have targeted a specific
wave, stage or stack by using a command like `cdk (diff|deploy) 'Wave1_Stage1_*'`, which would only deploy the stacks
in Wave1 Stage1.

</details>

```mermaid
graph TD
    subgraph Wave0["🌊 Wave1"]
        subgraph Wave0Stage0["🏗 Stage1"]
            StackWave1_Stage1_StackA["📦 StackA [1]"]
            StackWave1_Stage1_StackB["📦 StackB [2]"]
            StackWave1_Stage1_StackC["📦 StackC [2]"]
            StackWave1_Stage1_StackD["📦 StackD [3]"]
            StackWave1_Stage1_StackE["📦 StackE [2]"]
            StackWave1_Stage1_StackF["📦 StackF [1]"]
        end
        subgraph Wave0Stage1["🏗 Stage2"]
            StackWave1_Stage2_StackA["📦 StackA [1]"]
            StackWave1_Stage2_StackB["📦 StackB [1]"]
            StackWave1_Stage2_StackC["📦 StackC [2]"]
        end
    end
    StackWave1_Stage1_StackA --> StackWave1_Stage1_StackB
    StackWave1_Stage1_StackA --> StackWave1_Stage1_StackC
    StackWave1_Stage1_StackB --> StackWave1_Stage1_StackD
    StackWave1_Stage1_StackF --> StackWave1_Stage1_StackD
    StackWave1_Stage1_StackF --> StackWave1_Stage1_StackE
    StackWave1_Stage2_StackB --> StackWave1_Stage2_StackC
    subgraph Wave1["🌊 Wave2"]
        subgraph Wave1Stage0["🏗 Stage1"]
            StackWave2_Stage1_StackH["📦 StackH [1]"]
            StackWave2_Stage1_StackI["📦 StackI [1]"]
        end
        subgraph Wave1Stage1["🏗 Stage2"]
            StackWave2_Stage2_StackJ["📦 StackJ [1]"]
            StackWave2_Stage2_StackK["📦 StackK [1]"]
        end
    end
    subgraph Wave2["🌊 Wave3"]
        subgraph Wave2Stage0["🏗 Stage1"]
            StackWave3_Stage1_StackL["📦 StackL [1]"]
            StackWave3_Stage1_StackM["📦 StackM [1]"]
        end
        subgraph Wave2Stage1["🏗 Stage2"]
            StackWave3_Stage2_StackN["📦 StackN [1]"]
            StackWave3_Stage2_StackO["📦 StackO [1]"]
        end
        Wave2Stage0 --> Wave2Stage1
    end
    Wave0 --> Wave1
    Wave1 --> Wave2
```

## Options

### Separator

By default, the library uses an underscore (`_`) as the separator between Wave, Stage and Stack IDs. Not available in
the Legacy classes. This can be customized by passing a different separator to the `CdkExpressPipeline` constructor:

```python
const expressPipeline = new CdkExpressPipeline({
  separator: '-', // Now stack IDs will be like: Wave1-Stage1-StackA
});
```

### Sequential Stages

By default, stages within a wave are deployed in parallel. You can configure a wave to deploy its stages sequentially
by setting the `sequentialStages` option:

```python
const wave1 = expressPipeline.addWave('Wave1', {
  sequentialStages: true, // Stages in this wave will be deployed one after another
});
```

When a wave's stages are configured to be sequential, the wave will be marked with `[Seq 🏗️]` in the deployment order
output:

```plaintext
🌊 Wave1 [Seq 🏗️]
  🏗️ Stage1
    📦 StackA (Wave1_Stage1_StackA) [1]
  🏗️ Stage2
    📦 StackB (Wave1_Stage2_StackB) [1]
```

## Selective Deployment

Leverages a consistent and predictable naming convention for Stack IDs. A Stack ID consists of the Wave, Stage and
original Stack ID. This enables us to target Waves, Stages or individual stacks for deployment. For example, given the
following stack IDs:

```
Wave1_Stage1_StackA
Wave1_Stage1_StackB
Wave1_Stage1_StackC
Wave1_Stage2_StackD

Wave2_Stage1_StackE
Wave2_Stage1_StackF
```

It makes targeted deployments easy:

* Deploy Wave1: `cdk deploy 'Wave1_*'` deploys all stacks in `Wave1`
* Deploy Wave1 Stage1: `cdk deploy 'Wave1_Stage1_*'` deploys all stacks in `Wave1_Stage1`
* Deploy Wave1 Stage1 StackA: `cdk deploy 'Wave1_Stage1_StackA'` deploys only `Wave1_Stage1_StackA`

> [!IMPORTANT]
> When targeting specific stacks be sure to pass the `--exclusively` flag to the `cdk deploy` command to only deploy
> the specified stacks and not its dependencies.

Benefits of selecting a specific Wave, Stage or Stack over the all `'**'` method:

* While developing, you can speed up deployments from your local machine by deploying only what you are working on.
* When deploying with a CI/CD system, you can have additional logic between them. For example, you can place a
  manual approval step between `Wave1` and `Wave2`.

## Builds System Templates/Examples

### Local

These examples all assume a project created with the default structure of the CDK CLI
command `cdk init app --language typescript`.

These example are taken from the demo TS project: https://github.com/rehanvdm/cdk-express-pipeline-demo-ts

**Diff commands**

```bash
# Diffs all stacks
cdk diff '**' --profile YOUR_PROFILE
# Diffs only specific stacks in a Wave
cdk diff 'Wave1_*' --profile YOUR_PROFILE --exclusively
# Diffs only specific stacks of a Stage in a Wave
cdk diff 'Wave1_Stage1_*' --profile YOUR_PROFILE --exclusively
# Diffs only a specific stack
cdk diff 'Wave1_Stage1_StackA' --profile YOUR_PROFILE --exclusively
```

**Deploy commands**

```bash
# Deploys all stacks in correct order
cdk deploy '**' --profile YOUR_PROFILE --concurrency 10 --require-approval never
# Deploys only specific stacks in a Wave in correct order
cdk deploy 'Wave1_*' --profile YOUR_PROFILE --exclusively --concurrency 10 --require-approval never
# Deploys only specific stacks of a Stage in a Wave in correct order
cdk deploy 'Wave1_Stage1_*' --profile YOUR_PROFILE --exclusively --concurrency 10 --require-approval never
# Deploys only a specific stack
cdk deploy 'Wave1_Stage1_StackA' --profile YOUR_PROFILE --exclusively --concurrency 10 --require-approval never
```

### GitHub Workflows

These examples all assume a project created with the default structure of the CDK CLI
command `cdk init app --language typescript`.

These example are taken from the demo TS project: https://github.com/rehanvdm/cdk-express-pipeline-demo-ts

<details>
<summary>.github/workflows/diff.yml</summary>

Does a build and CDK Diff on PR open and push, the `cdk diff` output can be viewed in the action run logs.

```yaml
name: Diff
on:
  pull_request:
    types: [ opened, synchronize ]
  workflow_dispatch: { }

env:
  FORCE_COLOR: 1

jobs:
  deploy:
    name: CDK Diff and Deploy
    runs-on: ubuntu-latest
    permissions:
      actions: write
      contents: read
      id-token: write
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up node
        uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm install ci

      # TODO: Alternatively use an AWS IAM user and set the credentials in GitHub Secrets (less secure than GH OIDC below)
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: # TODO: Your role to assume
          aws-region: # TODO: your region

      - name: CDK diff
        run: npm run cdk -- diff '**'
```

Produces the following output in the GitHub Action logs:

![diff.png](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/_imgs/action_logs/diff.png)

</details><details>
<summary>.github/workflows/deploy.yml</summary>

Does a build, CDK Diff and Deploy when a push happens on the `main` branch.

```yaml
name: Deploy
on:
  push:
    branches:
      - main

env:
  FORCE_COLOR: 1

jobs:
  deploy:
    name: CDK Diff and Deploy
    runs-on: ubuntu-latest
    permissions:
      actions: write
      contents: read
      id-token: write
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up node
        uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm install ci

      # TODO: Alternatively use an AWS IAM user and set the credentials in GitHub Secrets (less secure than GH OIDC below)
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: # TODO: Your role to assume
          aws-region: # TODO: your region

      - name: CDK diff
        run: npm run cdk -- diff '**'

      - name: CDK deploy
        run: npm run cdk -- deploy '**' --require-approval never --concurrency 10
```

Produces the following output in the GitHub Action logs:

![diff.png](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/_imgs/action_logs/deploy.png)

</details><details>
<summary>.github/workflows/deploy-advance.yml</summary>

The `synth` job builds the CDK app and saves the cloud assembly to the `./cloud_assembly_output` directory. The whole
repo with installed NPM packages and the cloud assembly is then cached. This job of the pipeline does not have access
to any AWS Secrets, the installing of packages and building is decoupled from the deployment improving security.

The `wave1` and `wave2` jobs fetches the cloud assembly from the cache and then does a CDK Diff and Deploy on only their
stacks. The `wave1` job targets all the stacks that start with `Wave1_` and the `wave2` job targets all the stacks that
start with `Wave2_`. It is important to add the `--exclusively` flag to only focus on the specified stacks and not its
dependencies.

```yaml
name: Deploy Advance
on:
  push:
    branches:
      - main
  workflow_dispatch: { } # While testing only

env:
  FORCE_COLOR: 1

jobs:
  synth:
    name: Build and CDK Synth
    runs-on: ubuntu-latest
    permissions:
      actions: write

      contents: read
      id-token: write
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up node
        uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm install ci

      - name: CDK Synth
        run: npm run cdk -- synth --output ./cloud_assembly_output

      - name: Cache CDK Assets
        uses: actions/cache/save@v4
        with:
          path: ./
          key: "cdk-assets-${{ github.sha }}"

  wave1:
    name: Wave 1
    needs:
      - synth
    runs-on: ubuntu-latest
    permissions:
      actions: write
      contents: read
      id-token: write
    steps:
      - name: Fetch CDK Assets
        uses: actions/cache/restore@v4
        with:
          path: ./
          key: "cdk-assets-${{ github.sha }}"

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::581184285249:role/githuboidc-git-hub-deploy-role
          aws-region: eu-west-1

      - name: CDK diff
        run: npm run cdk -- diff 'Wave1_*' --exclusively --app ./cloud_assembly_output

      - name: CDK deploy
        run: npm run cdk -- deploy 'Wave1_*' --require-approval never --concurrency 10 --exclusively --app ./cloud_assembly_output

  # Manual approval

  wave2:
    name: Wave 2
    needs:
      - wave1
    runs-on: ubuntu-latest
    permissions:
      actions: write
      contents: read
      id-token: write
    steps:
      - name: Fetch CDK Assets
        uses: actions/cache/restore@v4
        with:
          path: ./
          key: "cdk-assets-${{ github.sha }}"

      # TODO: Alternatively use an AWS IAM user and set the credentials in GitHub Secrets (less secure than GH OIDC below)
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: # TODO: Your role to assume
          aws-region: # TODO: your region

      - name: CDK diff
        run: npm run cdk -- diff 'Wave2_*' --exclusively --app ./cloud_assembly_output

      - name: CDK deploy
        run: npm run cdk -- deploy 'Wave2_*' --require-approval never --concurrency 10 --exclusively --app ./cloud_assembly_output
```

Produces the following output in the GitHub Action logs:

![deploy_adv.png](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/_imgs/action_logs/deploy_adv.png)

![deploy_adv_1.png](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/_imgs/action_logs/deploy_adv_1.png)

</details>

## GitHub CI Workflow Generation

CDK Express Pipeline includes built-in GitHub CI workflow generation that automatically create GitHub
Actions workflows based on your pipeline configuration. This feature eliminates the need to manually write and maintain
GitHub workflow files.

### Basic Usage

To generate GitHub workflows, you need to specify a `GitHubWorkflowConfig` object when calling the
`generateGitHubWorkflows` method on your `CdkExpressPipeline` instance. This configuration defines how the workflows
should be structured, including build, synth, diff, and deploy commands.

This basic example assumes that you only have one environment/AWS account named `prod`. A CDK diff will be created on pull request
to the `main` branch, and a CDK deploy will be created on push action to the `main` branch. You can customize the
configuration to suit your needs, including multiple environments, custom build processes, and more.

```python
import { CdkExpressPipeline, GitHubWorkflowConfig } from 'cdk-express-pipeline';

// Define your pipeline (as shown in Usage section)
const app = new App();
const pipeline = new CdkExpressPipeline();
// ... add waves, stages, and stacks ...

// Define GitHub workflow configuration
const ghConfig: GitHubWorkflowConfig = {
  synth: {
    buildConfig: {
      type: 'preset-npm', // or 'workflow' to specify a GitHub workflow file for custom build process
    },
    commands: [
      { prod: "npm run cdk -- synth '**'" },
    ],
  },
  diff: [{
    on: {
      pullRequest: {
        branches: ['main'],
      },
    },
    stackSelector: 'stage',
    writeAsComment: true,
    assumeRoleArn: 'arn:aws:iam::123456789012:role/github-oidc-role',
    assumeRegion: 'us-east-1',
    commands: [
      { prod: 'npm run cdk -- diff {stackSelector}' },
    ],
  }],
  deploy: [{
    on: {
      push: {
        branches: ['main'],
      },
    },
    stackSelector: 'stage',
    assumeRoleArn: 'arn:aws:iam::123456789012:role/github-oidc-role',
    assumeRegion: 'us-east-1',
    commands: [
      { prod: 'npm run cdk -- deploy {stackSelector} --concurrency 10 --require-approval never --exclusively' },
    ],
  }],
};

// Generate workflows and save them (by specifying the `true` argument)
await pipeline.generateGitHubWorkflows(ghConfig, true);
```

The workflow generation creates the following files in your `.github` directory:

```
.github/
├── actions/
│   ├── cdk-express-pipeline-synth/
│   │   └── action.yml
│   ├── cdk-express-pipeline-diff/
│   │   └── action.yml
│   └── cdk-express-pipeline-deploy/
│       └── action.yml
└── workflows/
    ├── cdk-express-pipeline-diff.yml
    └── cdk-express-pipeline-deploy-prod.yml
```

### Configuration Options

#### Synth Configuration

The `synth` configuration defines how your CDK application is built and synthesized:

```python
synth: {
  buildConfig: {
    type: 'preset-npm', // Built-in npm build process
    // OR
    type: 'workflow',
    workflow: {
      path: '.github/actions/build', // Path to custom workflow
    },
  },
  commands: [
    { prod: "npm run cdk -- synth '**'" },
  ],
}
```

The `buildConfig` can use a built-in preset (like `preset-npm`) which uses the standard NPM build process GitHub
Action steps, installing node and then npm install. Alternatively, you can specify a **reusable action** that defines a
custom workflow in native GitHub Actions format, allowing for a more complex build processes. Like building
assets in parallel, pushing to container registries etc. For example:

```yaml
# .github/actions/build/action.yml
name: Custom Build
description: Only needed if Synth build step is set to 'workflow'. When able, use the `preset-` instead
runs:
  using: composite
  steps:
    - name: Set up node
      uses: actions/setup-node@v4
      with:
        node-version: 20
        cache: npm
    - name: Install dependencies
      run: npm ci
      shell: bash

    # Additional steps to build Applications that are referenced in the CDK app
```

The `commands` array defines the commands to run for synthesizing your CDK application. This allows you to generate
multiple CDK cloud assemblies for different environments (e.g., dev, prod) by using environment-specific commands.

This example assumes this is done with `env` [CDK context variable](https://docs.aws.amazon.com/cdk/v2/guide/context.html#context-cli)
and shows how to generate two different cloud assemblies for `dev` and `prod` environments and store there output in
separate directories within the `cdk.out` directory.

> [!IMPORTANT]
> These commands must still place these cloud assemblies in the `cdk.out` directory. The `cdk.out` and `node_modules`
> will be cached and restored on workflow jobs within diff and deploy.

```python
synth: {
  commands: [
    {dev: "npm run cdk -- synth '**' -c env=dev --output=cdk.out/dev"},
    {prod: "npm run cdk -- synth '**' -c env=prod --output=cdk.out/prod"},
  ]
}
```

#### Diff Configuration

The `diff` configuration defines when and how CDK diff operations are performed:

```python
diff: [{
  on: {
    pullRequest: {
      branches: ['main', 'develop'],
    },
    // OR
    push: {
      branches: ['main'],
    },
  },
  stackSelector: 'stage', // 'wave', 'stage', or 'stack'
  writeAsComment: true, // Write diff output as PR comment
  assumeRoleArn: 'arn:aws:iam::123456789012:role/github-oidc-role',
  assumeRegion: 'us-east-1',
  commands: [
    { prod: 'npm run cdk -- diff {stackSelector}' },
  ],
}]
```

> [!IMPORTANT]
> These commands must include the {stackSelector} string that gets replaced dynamically.

The `on` field specifies the events that trigger the diff operation, you would most likely always want to trigger this
on pull requests. The `writeAsComment` property uses the [corymhall/cdk-diff-action@v2](https://github.com/corymhall/cdk-diff-action)
Action to write the diff output as a comment on the pull request. This is useful for reviewing changes before merging.

See the [Stack Selectors](#stack-selectors) section below for details on the `stackSelector` option. The `assumeRoleArn`
and `assumeRegion` options are used to configure the [AWS OIDC authentication](https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
for the GitHub Actions workflow, allowing it to assume a role in your AWS account securely when doing `commands`.

#### Deploy Configuration

The `deploy` configuration defines when and how CDK deploy operations are performed:

```python
deploy: [{
  on: {
    pullRequest: {
      branches: ['main'],
    },
  },
  stackSelector: 'stack', // 'wave', 'stage', or 'stack'
  assumeRoleArn: 'arn:aws:iam::123456789012:role/github-oidc-role',
  assumeRegion: 'us-east-1',
  commands: [
    { prod: 'npm run cdk -- deploy {stackSelector} --concurrency 10 --require-approval never --exclusively' },
  ],
}]
```

> [!IMPORTANT]
> These commands must include the {stackSelector} string that gets replaced dynamically.

The `on` field specifies the events that trigger the deploy operation, you would most likely always want to trigger this
on pushes or on tag creation.

See the [Stack Selectors](#stack-selectors) section below for details on the `stackSelector` option. The `assumeRoleArn`
and `assumeRegion` options are used to configure the [AWS OIDC authentication](https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
for the GitHub Actions workflow, allowing it to assume a role in your AWS account securely when doing the `commands`.

### Stack Selectors

The `stackSelector` option determines how stacks are targeted in diff and deploy operations:

* **`'wave'`**: Will create a GitHun Job in the Workflow for each wave (e.g., `Wave1_*`)
* **`'stage'`**: Will create a GitHun Job in the Workflow for each wave and stage combination (e.g., `Wave1_Stage1_*`)
* **`'stack'`**: Will create a GitHun Job in the Workflow for each wave, stage and stack combination (e.g., `Wave1_Stage1_Stack1`)

The `{stackSelector}` placeholder in commands is automatically replaced with the appropriate pattern as shown above.

Using `stack` is the most granular, but it will spawn a separate job for each stack, which may not be ideal for larger
pipelines as this adds a bit of overhead. Each job needs to fetch the `cdk.out` (cloud assembly) and `node_modules` from the
cache, which can additional time, and thus cost. This might become an issue in pipelines with large assets and many stacks.

Recommended defaults:

* `diff` config: `'stage'` is a good balance between granularity and performance as each job will post a GitHub comment
  if `writeAsComment` is set to `true`.
* `deploy` config: `'stack'` is recommended so that each job only shows the CFN deployment logs for that stack and the
  job can be retried if it fails without affecting other stacks.

### Advanced Features

#### Multiple Environments

Both `diff` and `deploy` configurations accept arrays. This allows you to define multiple workflows for different
environments or deployment strategies.

This example:

* Assumes that the `main` branch is linked to the `development` AWS environment/account and the `prod` branch is linked
  to the `production` environment.
* Do both `staging` and `production` diffs on PRs to the `main` branch. So that we can also see the changes that will
  be deployed to production when making this PR to staging.
* Do a `production` diff on PRs to the `production` branch.
* Defines separate deploy workflows for `development` and `production` when pushing to the `main` and `production`
  branches, respectively.

```python
const ghConfig: GitHubWorkflowConfig = {
 synth: {
   buildConfig: {
     type: 'preset-npm',
   },
   commands: [
     { development: "npm run cdk -- synth '**' -c env=development --output=cdk.out/development" },
     { production: "npm run cdk -- synth '**' -c env=production --output=cdk.out/production" },
   ],
 },
 diff: [
   {
     id: 'development',
     on: {
       pullRequest: {
         branches: ['main'],
       },
     },
     stackSelector: 'stage',
     writeAsComment: true,
     assumeRoleArn: 'arn:aws:iam::123456789012:role/github-oidc-role',
     assumeRegion: 'us-east-1',
     commands: [
       { development: 'npm run cdk -- diff {stackSelector} --app=cdk.out/development' },
       { production: 'npm run cdk -- diff {stackSelector} --app=cdk.out/production' },
     ],
   },
   {
     id: 'production',
     on: {
       pullRequest: {
         branches: ['production'],
       },
     },
     stackSelector: 'stage',
     writeAsComment: true,
     assumeRoleArn: 'arn:aws:iam::123456789012:role/github-oidc-role',
     assumeRegion: 'us-east-1',
     commands: [
       { production: 'npm run cdk -- diff {stackSelector} --app=cdk.out/production' },
     ],
   },
 ],
 deploy: [
   {
     id: 'development',
     on: {
       push: {
         branches: ['main'],
       },
     },
     stackSelector: 'stack',
     assumeRoleArn: 'arn:aws:iam::123456789012:role/github-oidc-role',
     assumeRegion: 'us-east-1',
     commands: [
       { development: 'npm run cdk -- deploy {stackSelector} --concurrency 10 --require-approval never --exclusively --app=cdk.out/development' },
     ],
   },
   {
     id: 'production',
     on: {
       push: {
         branches: ['production'],
       },
     },
     stackSelector: 'stack',
     assumeRoleArn: 'arn:aws:iam::123456789012:role/github-oidc-role',
     assumeRegion: 'us-east-1',
     commands: [
       { production: 'npm run cdk -- deploy {stackSelector} --concurrency 10 --require-approval never --exclusively --app=cdk.out/production' },
     ],
   },
 ],
}
```

The `ids` for the `diff` and `deploy` objects are used to generate unique workflow file names in the
`.github/workflows` directory. For example, these files will be generated (along with the reusable actions in the
`.github/actions` directory):

```
.github/
├── actions/
│   ├── cdk-express-pipeline-synth/
│   │   └── action.yml
│   ├── cdk-express-pipeline-diff/
│   │   └── action.yml
│   └── cdk-express-pipeline-deploy/
│       └── action.yml
└── workflows/
    ├── cdk-express-pipeline-diff-development.yml
    ├── cdk-express-pipeline-diff-production.yml
    ├── cdk-express-pipeline-deploy-development.yml
    └── cdk-express-pipeline-deploy-production.yml
```

#### Workflow Customization

The generated workflows can be customized using JSON Patch operations:

```python
import { CdkExpressPipeline, GitHubWorkflowConfig } from 'cdk-express-pipeline';

// Define your pipeline (as shown in Usage section)
const app = new App();
const pipeline = new CdkExpressPipeline();
// ... add waves, stages, and stacks ...

// Define GitHub workflow configuration
const ghConfig: GitHubWorkflowConfig = {
  ...
};

const ghWorkflows = await pipeline.generateGitHubWorkflows(ghConfig, false);
for (let w = 0; w < ghWorkflows.length; w++) {
  if (ghWorkflows[w].fileName === 'workflows/cdk-express-pipeline-deploy-dev.yml') {
    ghWorkflows[w]?.content.patch(
      // Change the concurrency of the deploy dev workflow
      JsonPatch.replace('/concurrency/cancel-in-progress', true),
      //Add an extra step to the build job that echos success
      JsonPatch.add('/jobs/build/steps/-', {
        name: 'Echo Success',
        shell: 'bash',
        run: 'echo "Build succeeded!"',
      }),
    );
  }
}

pipeline.saveGitHubWorkflows(ghWorkflows);
```

The JSON object of the workflow can be modified using the `JsonPatch` class, which provides the following methods:

* `add(path, value)`: Adds a value to an object or inserts it into an array. In the case of an
  array, the value is inserted before the given index. The `-` character can be
  used instead of an index to insert at the end of an array.
  Ex: `JsonPatch.add('/milk', true) JsonPatch.add('/biscuits/1', { "name": "Ginger Nut" })`
* `remove(path)`: Removes a value from an object or array.
  Ex: `JsonPatch.remove('/biscuits') JsonPatch.remove('/biscuits/0')`
* `replace(path, value)`: Replaces a value. Equivalent to a “remove” followed by an “add”.
  Ex: `JsonPatch.replace('/biscuits/0/name', 'Chocolate Digestive')`
* `copy(from, path)`: Copies a value from one location to another within the JSON document. Both
  from and path are JSON Pointers.
  Ex: `JsonPatch.copy('/biscuits/0', '/best_biscuit')`
* `move(from, path)`: Moves a value from one location to the other. Both from and path are JSON Pointers.
  Ex: `JsonPatch.move('/biscuits', '/cookies')`
* `test(path, value)`: Tests that the specified value is set in the document. If the test fails,
  then the patch as a whole should not apply.
  Ex: `JsonPatch.test('/best_biscuit/name', 'Choco Leibniz')`

### GitLab

TODO...

### Any other build system

...

## Legacy Usage

The `CdkExpressPipelineLegacy` class can be used when you do not want/can not use the `ExpressStack` class and have to
stick to the CDK `Stack` class.

> [!WARNING]
> Always use non-legacy classes for greenfield projects. Only use the Legacy classes if you have no other choice.

The following features are not available when using the Legacy classes:

* Enforcing Wave, Stage and Stack names do not include the `separator` character.
* Enforcing that a Stack in Stage 1 can not depend on a Stack in Stage 2.
* Printing stack dependencies within a Stage. Since we do not know what stage a stack belongs to, it's not possible to
  print the dependencies of stacks of only that stage and not others.
* If a consistent naming convention has not been followed for Stacks, it might not be possible to target all stacks in a
  stage or a wave. Deployment will have to always target all stacks with `"**"`.
* Stack ids are not changed and have to be unique across all stacks in the CDK app, whereas with the non-legacy
  classes, stack ids only have to be unique within a Wave.

**Stack Definition:**

```python
class StackA extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new cdk.aws_sns.Topic(this, 'MyTopicA');
    // ... more resources
  }
}

class StackB extends cdk.Stack {
  // ... similar to StackA
}

class StackC extends cdk.Stack {

}
```

**1️⃣ Pipeline Definition:**

```python
const app = new App();
const expressPipeline = new CdkExpressPipelineLegacy();

/* === Wave 1 === */
/* --- Wave 1, Stage 1--- */
const stackA = new StackA(app, 'StackA');
const stackB = new StackB(app, 'StackB');
stackB.addDependency(stackA);

// === Wave 2 ===
/* --- Wave 2, Stage 1--- */
const stackC = new StackC(app, 'StackC');

expressPipeline.synth([
  {
    id: 'Wave1',
    stages: [{
      id: 'Stage1',
      stacks: [
        stackA,
        stackB,
      ],
    }],
  },
  {
    id: 'Wave2',
    stages: [{
      id: 'Stage1',
      stacks: [
        stackC,
      ],
    }],
  },
]);
```

The stack deployment order will be printed to the console when running `cdk` commands:

```plaintext
ORDER OF DEPLOYMENT
🌊 Waves  - Deployed sequentially.
🏗️ Stages - Deployed in parallel by default, unless the wave is marked `[Seq 🏗️]` for sequential stage execution.
📦 Stacks - Deployed after their dependent stacks within the stage (dependencies shown below them with ↳).
           - Lines prefixed with a pipe (|) indicate stacks matching the CDK pattern.
           - Stack deployment order within the stage is shown in square brackets (ex: [1])

🌊 Wave1
  🏗️ Stage1
    📦 StackA
    📦 StackB
🌊 Wave2
  🏗️ Stage1
    📦 StackC
```

<details>
<summary><b>2️⃣ Pipeline Definition Alternative - method builder:</b></summary>

```python
const app = new App();
const expressPipeline = new CdkExpressPipelineLegacy();

/* === Wave 1 === */
const wave1 = expressPipeline.addWave('Wave1');
/* --- Wave 1, Stage 1--- */
const wave1Stage1 = wave1.addStage('Stage1');
const stackA = wave1Stage1.addStack(new StackA(app, 'StackA'));
const stackB = wave1Stage1.addStack(new StackB(app, 'StackB'));
stackB.addDependency(stackA);

// === Wave 2 ===
const wave2 = expressPipeline.addWave('Wave2');
/* --- Wave 2, Stage 1--- */
const wave2Stage1 = wave2.addStage('Stage1');
wave2Stage1.addStack(new StackC(app, 'StackC'));

expressPipeline.synth([
  wave1,
  wave2,
]);
```

</details>

## Demo Projects

* [CDK Express Pipeline Demo TS](https://github.com/rehanvdm/cdk-express-pipeline-demo-ts)
* [CDK Express Pipeline Demo Python](https://github.com/rehanvdm/cdk-express-pipeline-demo-python)

## Docs

* [FAQ](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/FAQ.md)
* [Projen Sacrifices](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/docs/Projen%20Sacrifices.md)
* [API](https://github.com/rehanvdm/cdk-express-pipeline/blob/main/API.md)
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="cdk-express-pipeline.BuildConfig",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "workflow": "workflow"},
)
class BuildConfig:
    def __init__(
        self,
        *,
        type: builtins.str,
        workflow: typing.Optional[typing.Union["WorkflowLocation", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param type: The type of workflow to use.
        :param workflow: Only required if type is 'workflow'. Specify the workflow or reusable action to use for building
        '''
        if isinstance(workflow, dict):
            workflow = WorkflowLocation(**workflow)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__176a33dbfec3fbf84c7f09cd7d5fa47dc7938b65faf1fefd2a2e277c8b10b538)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument workflow", value=workflow, expected_type=type_hints["workflow"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if workflow is not None:
            self._values["workflow"] = workflow

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of workflow to use.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def workflow(self) -> typing.Optional["WorkflowLocation"]:
        '''Only required if type is 'workflow'.

        Specify the workflow or reusable action to use for building
        '''
        result = self._values.get("workflow")
        return typing.cast(typing.Optional["WorkflowLocation"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BuildConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CdkExpressPipeline(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.CdkExpressPipeline",
):
    '''A CDK Express Pipeline that defines the order in which the stacks are deployed.'''

    def __init__(
        self,
        *,
        separator: typing.Optional[builtins.str] = None,
        waves: typing.Optional[typing.Sequence["ExpressWave"]] = None,
    ) -> None:
        '''
        :param separator: Separator between the wave, stage and stack ids that are concatenated to form the stack id. Default: _
        :param waves: The waves in the pipeline.
        '''
        props = CdkExpressPipelineProps(separator=separator, waves=waves)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="addWave")
    def add_wave(
        self,
        id: builtins.str,
        sequential_stages: typing.Optional[builtins.bool] = None,
    ) -> "IExpressWave":
        '''Add a wave to the pipeline.

        :param id: The wave identifier.
        :param sequential_stages: If true, the stages in the wave will be executed sequentially. Default: false.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51d5a812c29abca46e9446db3e0acfaedb3fb0f70a5ccbc26b8b26b62c731b30)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument sequential_stages", value=sequential_stages, expected_type=type_hints["sequential_stages"])
        return typing.cast("IExpressWave", jsii.invoke(self, "addWave", [id, sequential_stages]))

    @jsii.member(jsii_name="generateGitHubWorkflows")
    def generate_git_hub_workflows(
        self,
        git_hub_workflow_config: typing.Union["GitHubWorkflowConfig", typing.Dict[builtins.str, typing.Any]],
        save_to_files: typing.Optional[builtins.bool] = None,
    ) -> typing.List["GithubWorkflowFile"]:
        '''
        :param git_hub_workflow_config: -
        :param save_to_files: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e284e6bc2289754ab5a16d412952ff0c2b3c0f4ae78655914206f911311579c0)
            check_type(argname="argument git_hub_workflow_config", value=git_hub_workflow_config, expected_type=type_hints["git_hub_workflow_config"])
            check_type(argname="argument save_to_files", value=save_to_files, expected_type=type_hints["save_to_files"])
        return typing.cast(typing.List["GithubWorkflowFile"], jsii.invoke(self, "generateGitHubWorkflows", [git_hub_workflow_config, save_to_files]))

    @jsii.member(jsii_name="generateMermaidDiagram")
    def generate_mermaid_diagram(
        self,
        waves: typing.Sequence["IExpressWave"],
    ) -> builtins.str:
        '''Generate a Mermaid diagram showing the deployment order.

        :param waves: The waves to include in the diagram.

        :private: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48596730e21a3fe0e78a5e73d024ad054e1679fbe0d63f873eb81c728a6fc0d6)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        return typing.cast(builtins.str, jsii.invoke(self, "generateMermaidDiagram", [waves]))

    @jsii.member(jsii_name="printWaves")
    def print_waves(self, waves: typing.Sequence["IExpressWave"]) -> None:
        '''Print the order of deployment to the console.

        :param waves: -

        :private: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e18d77fb9496cb5fdeabb0fe5a14c3dcd08b7a4747694ac0a799b01dfa105a34)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        return typing.cast(None, jsii.invoke(self, "printWaves", [waves]))

    @jsii.member(jsii_name="saveGitHubWorkflows")
    def save_git_hub_workflows(
        self,
        workflows: typing.Sequence[typing.Union["GithubWorkflowFile", typing.Dict[builtins.str, typing.Any]]],
    ) -> None:
        '''
        :param workflows: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a545be0c7f0244a8cedbc9796c6c38f57f873c3c1ba9bb23a76f5d8f63bfafa)
            check_type(argname="argument workflows", value=workflows, expected_type=type_hints["workflows"])
        return typing.cast(None, jsii.invoke(self, "saveGitHubWorkflows", [workflows]))

    @jsii.member(jsii_name="synth")
    def synth(
        self,
        waves: typing.Optional[typing.Sequence["IExpressWave"]] = None,
        print: typing.Optional[builtins.bool] = None,
        *,
        file_name: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Synthesize the pipeline which creates the dependencies between the stacks in the correct order.

        :param waves: The waves to synthesize.
        :param print: Whether to print the order of deployment to the console.
        :param file_name: Must end in ``.md``. If not provided, defaults to cdk-express-pipeline-deployment-order.md.
        :param path: The path where the Mermaid diagram will be saved. If not provided defaults to root
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddf3f54429b9cebdd63080df8e42a8f0bee80ea5889f7848d8110f99befcf433)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
            check_type(argname="argument print", value=print, expected_type=type_hints["print"])
        save_mermaid_diagram = MermaidDiagramOutput(file_name=file_name, path=path)

        return typing.cast(None, jsii.invoke(self, "synth", [waves, print, save_mermaid_diagram]))

    @builtins.property
    @jsii.member(jsii_name="waves")
    def waves(self) -> typing.List["IExpressWave"]:
        return typing.cast(typing.List["IExpressWave"], jsii.get(self, "waves"))


class CdkExpressPipelineLegacy(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.CdkExpressPipelineLegacy",
):
    '''A CDK Express Pipeline that defines the order in which the stacks are deployed.

    This is the legacy version of the pipeline that uses the ``Stack`` class, for plug and play compatibility with existing CDK projects that can not
    use the ``ExpressStack`` class. For new projects, use the ``CdkExpressPipeline`` class.
    '''

    def __init__(
        self,
        waves: typing.Optional[typing.Sequence["IExpressWaveLegacy"]] = None,
    ) -> None:
        '''
        :param waves: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e78d8fa8554a29ac59173413b98062741ae83aeb4754f02a80c85c27e16d8ce)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        jsii.create(self.__class__, self, [waves])

    @jsii.member(jsii_name="addWave")
    def add_wave(
        self,
        id: builtins.str,
        sequential_stages: typing.Optional[builtins.bool] = None,
    ) -> "ExpressWaveLegacy":
        '''Add a wave to the pipeline.

        :param id: The wave identifier.
        :param sequential_stages: If true, the stages in the wave will be executed sequentially. Default: false.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58733341409ff8a6c60fbf06de891a31f81f41cf55e7503aaa0238ee46ff5166)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument sequential_stages", value=sequential_stages, expected_type=type_hints["sequential_stages"])
        return typing.cast("ExpressWaveLegacy", jsii.invoke(self, "addWave", [id, sequential_stages]))

    @jsii.member(jsii_name="generateMermaidDiagram")
    def generate_mermaid_diagram(
        self,
        waves: typing.Sequence["IExpressWaveLegacy"],
    ) -> builtins.str:
        '''Generate a Mermaid diagram showing the deployment order.

        :param waves: The waves to include in the diagram.

        :private: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1ef4d18ff1ca1a7788d1801361a996c26480f2387d3a28be69812108f489380)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        return typing.cast(builtins.str, jsii.invoke(self, "generateMermaidDiagram", [waves]))

    @jsii.member(jsii_name="printWaves")
    def print_waves(self, waves: typing.Sequence["IExpressWaveLegacy"]) -> None:
        '''Print the order of deployment to the console.

        :param waves: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d22fe922729d650ca61abf0f4568bb8cbafe791434481f3e0cce74d098f785e)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        return typing.cast(None, jsii.invoke(self, "printWaves", [waves]))

    @jsii.member(jsii_name="synth")
    def synth(
        self,
        waves: typing.Optional[typing.Sequence["IExpressWaveLegacy"]] = None,
        print: typing.Optional[builtins.bool] = None,
        *,
        file_name: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Synthesize the pipeline which creates the dependencies between the stacks in the correct order.

        :param waves: The waves to synthesize.
        :param print: Whether to print the order of deployment to the console.
        :param file_name: Must end in ``.md``. If not provided, defaults to cdk-express-pipeline-deployment-order.md.
        :param path: The path where the Mermaid diagram will be saved. If not provided defaults to root
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c7d8bd5a65c1437ed17046edfb50f14e1f2b8f73c9db08927132a10f37d409d)
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
            check_type(argname="argument print", value=print, expected_type=type_hints["print"])
        save_mermaid_diagram = MermaidDiagramOutput(file_name=file_name, path=path)

        return typing.cast(None, jsii.invoke(self, "synth", [waves, print, save_mermaid_diagram]))

    @builtins.property
    @jsii.member(jsii_name="waves")
    def waves(self) -> typing.List["IExpressWaveLegacy"]:
        return typing.cast(typing.List["IExpressWaveLegacy"], jsii.get(self, "waves"))

    @waves.setter
    def waves(self, value: typing.List["IExpressWaveLegacy"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54082bd27a8ceffd74f1b6a0cb05b3bbcf4ffa9ada94c72e52e645687ad4ad5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "waves", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="cdk-express-pipeline.CdkExpressPipelineProps",
    jsii_struct_bases=[],
    name_mapping={"separator": "separator", "waves": "waves"},
)
class CdkExpressPipelineProps:
    def __init__(
        self,
        *,
        separator: typing.Optional[builtins.str] = None,
        waves: typing.Optional[typing.Sequence["ExpressWave"]] = None,
    ) -> None:
        '''
        :param separator: Separator between the wave, stage and stack ids that are concatenated to form the stack id. Default: _
        :param waves: The waves in the pipeline.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc99a79d5da23f439f19b4717a315983fa455ec2ae7d0300ac3d7381d5892205)
            check_type(argname="argument separator", value=separator, expected_type=type_hints["separator"])
            check_type(argname="argument waves", value=waves, expected_type=type_hints["waves"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if separator is not None:
            self._values["separator"] = separator
        if waves is not None:
            self._values["waves"] = waves

    @builtins.property
    def separator(self) -> typing.Optional[builtins.str]:
        '''Separator between the wave, stage and stack ids that are concatenated to form the stack id.

        :default: _
        '''
        result = self._values.get("separator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def waves(self) -> typing.Optional[typing.List["ExpressWave"]]:
        '''The waves in the pipeline.'''
        result = self._values.get("waves")
        return typing.cast(typing.Optional[typing.List["ExpressWave"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CdkExpressPipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.DeployWorkflowConfig",
    jsii_struct_bases=[],
    name_mapping={
        "assume_region": "assumeRegion",
        "assume_role_arn": "assumeRoleArn",
        "commands": "commands",
        "on": "on",
        "stack_selector": "stackSelector",
        "id": "id",
    },
)
class DeployWorkflowConfig:
    def __init__(
        self,
        *,
        assume_region: builtins.str,
        assume_role_arn: builtins.str,
        commands: typing.Sequence[typing.Mapping[builtins.str, builtins.str]],
        on: typing.Union["WorkflowTriggers", typing.Dict[builtins.str, typing.Any]],
        stack_selector: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param assume_region: AWS region to assume for the diff operation.
        :param assume_role_arn: ARN of the role to assume for the diff operation.
        :param commands: Commands to run for synthesis.
        :param on: Conditions that trigger the deploy workflow.
        :param stack_selector: Selector for the stack type.
        :param id: Unique identifier, postfixed to the generated workflow name. Can be omitted if only one workflow is specified.
        '''
        if isinstance(on, dict):
            on = WorkflowTriggers(**on)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__064ff6a399a517de1d9d8831492460b92378a4013ef6125878a1c1553dab6e74)
            check_type(argname="argument assume_region", value=assume_region, expected_type=type_hints["assume_region"])
            check_type(argname="argument assume_role_arn", value=assume_role_arn, expected_type=type_hints["assume_role_arn"])
            check_type(argname="argument commands", value=commands, expected_type=type_hints["commands"])
            check_type(argname="argument on", value=on, expected_type=type_hints["on"])
            check_type(argname="argument stack_selector", value=stack_selector, expected_type=type_hints["stack_selector"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "assume_region": assume_region,
            "assume_role_arn": assume_role_arn,
            "commands": commands,
            "on": on,
            "stack_selector": stack_selector,
        }
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def assume_region(self) -> builtins.str:
        '''AWS region to assume for the diff operation.'''
        result = self._values.get("assume_region")
        assert result is not None, "Required property 'assume_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def assume_role_arn(self) -> builtins.str:
        '''ARN of the role to assume for the diff operation.'''
        result = self._values.get("assume_role_arn")
        assert result is not None, "Required property 'assume_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commands(self) -> typing.List[typing.Mapping[builtins.str, builtins.str]]:
        '''Commands to run for synthesis.'''
        result = self._values.get("commands")
        assert result is not None, "Required property 'commands' is missing"
        return typing.cast(typing.List[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def on(self) -> "WorkflowTriggers":
        '''Conditions that trigger the deploy workflow.'''
        result = self._values.get("on")
        assert result is not None, "Required property 'on' is missing"
        return typing.cast("WorkflowTriggers", result)

    @builtins.property
    def stack_selector(self) -> builtins.str:
        '''Selector for the stack type.'''
        result = self._values.get("stack_selector")
        assert result is not None, "Required property 'stack_selector' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Unique identifier, postfixed to the generated workflow name.

        Can be omitted if only one workflow is specified.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DeployWorkflowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.DiffWorkflowConfig",
    jsii_struct_bases=[],
    name_mapping={
        "assume_region": "assumeRegion",
        "assume_role_arn": "assumeRoleArn",
        "commands": "commands",
        "on": "on",
        "stack_selector": "stackSelector",
        "id": "id",
        "write_as_comment": "writeAsComment",
    },
)
class DiffWorkflowConfig:
    def __init__(
        self,
        *,
        assume_region: builtins.str,
        assume_role_arn: builtins.str,
        commands: typing.Sequence[typing.Mapping[builtins.str, builtins.str]],
        on: typing.Union["WorkflowTriggers", typing.Dict[builtins.str, typing.Any]],
        stack_selector: builtins.str,
        id: typing.Optional[builtins.str] = None,
        write_as_comment: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param assume_region: AWS region to assume for the diff operation.
        :param assume_role_arn: ARN of the role to assume for the diff operation.
        :param commands: Commands to run for synthesis.
        :param on: Conditions that trigger the diff workflow.
        :param stack_selector: Selector for the stack type.
        :param id: Unique identifier, postfixed to the generated workflow name. Can be omitted if only one workflow is specified.
        :param write_as_comment: Whether to write the diff as a comment. Default: true
        '''
        if isinstance(on, dict):
            on = WorkflowTriggers(**on)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fd8d22f0c989f84b5e91067c258f24562fc4d3b5c471e9302c3fd36c7c66492)
            check_type(argname="argument assume_region", value=assume_region, expected_type=type_hints["assume_region"])
            check_type(argname="argument assume_role_arn", value=assume_role_arn, expected_type=type_hints["assume_role_arn"])
            check_type(argname="argument commands", value=commands, expected_type=type_hints["commands"])
            check_type(argname="argument on", value=on, expected_type=type_hints["on"])
            check_type(argname="argument stack_selector", value=stack_selector, expected_type=type_hints["stack_selector"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument write_as_comment", value=write_as_comment, expected_type=type_hints["write_as_comment"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "assume_region": assume_region,
            "assume_role_arn": assume_role_arn,
            "commands": commands,
            "on": on,
            "stack_selector": stack_selector,
        }
        if id is not None:
            self._values["id"] = id
        if write_as_comment is not None:
            self._values["write_as_comment"] = write_as_comment

    @builtins.property
    def assume_region(self) -> builtins.str:
        '''AWS region to assume for the diff operation.'''
        result = self._values.get("assume_region")
        assert result is not None, "Required property 'assume_region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def assume_role_arn(self) -> builtins.str:
        '''ARN of the role to assume for the diff operation.'''
        result = self._values.get("assume_role_arn")
        assert result is not None, "Required property 'assume_role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def commands(self) -> typing.List[typing.Mapping[builtins.str, builtins.str]]:
        '''Commands to run for synthesis.'''
        result = self._values.get("commands")
        assert result is not None, "Required property 'commands' is missing"
        return typing.cast(typing.List[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def on(self) -> "WorkflowTriggers":
        '''Conditions that trigger the diff workflow.'''
        result = self._values.get("on")
        assert result is not None, "Required property 'on' is missing"
        return typing.cast("WorkflowTriggers", result)

    @builtins.property
    def stack_selector(self) -> builtins.str:
        '''Selector for the stack type.'''
        result = self._values.get("stack_selector")
        assert result is not None, "Required property 'stack_selector' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Unique identifier, postfixed to the generated workflow name.

        Can be omitted if only one workflow is specified.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def write_as_comment(self) -> typing.Optional[builtins.bool]:
        '''Whether to write the diff as a comment.

        :default: true
        '''
        result = self._values.get("write_as_comment")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DiffWorkflowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.ExpressWaveProps",
    jsii_struct_bases=[],
    name_mapping={"id": "id", "separator": "separator"},
)
class ExpressWaveProps:
    def __init__(
        self,
        *,
        id: builtins.str,
        separator: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param id: 
        :param separator: Separator between the wave, stage and stack ids that are concatenated to form the stack id. Default: ``_``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d91dc79595e990d6da1a185afde4e65465da1f5dc12abd5220e16803db5481a2)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument separator", value=separator, expected_type=type_hints["separator"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "id": id,
        }
        if separator is not None:
            self._values["separator"] = separator

    @builtins.property
    def id(self) -> builtins.str:
        result = self._values.get("id")
        assert result is not None, "Required property 'id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def separator(self) -> typing.Optional[builtins.str]:
        '''Separator between the wave, stage and stack ids that are concatenated to form the stack id.

        :default: ``_``
        '''
        result = self._values.get("separator")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ExpressWaveProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.GitHubWorkflowConfig",
    jsii_struct_bases=[],
    name_mapping={"deploy": "deploy", "diff": "diff", "synth": "synth"},
)
class GitHubWorkflowConfig:
    def __init__(
        self,
        *,
        deploy: typing.Sequence[typing.Union[DeployWorkflowConfig, typing.Dict[builtins.str, typing.Any]]],
        diff: typing.Sequence[typing.Union[DiffWorkflowConfig, typing.Dict[builtins.str, typing.Any]]],
        synth: typing.Union["SynthWorkflowConfig", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param deploy: Configuration for the deploy workflow.
        :param diff: Configuration for the diff workflow.
        :param synth: Configuration for the synth workflow.
        '''
        if isinstance(synth, dict):
            synth = SynthWorkflowConfig(**synth)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a08064d282d091b65891b01b014a0a8a260163ad7f73ec21450a321e2a8b285)
            check_type(argname="argument deploy", value=deploy, expected_type=type_hints["deploy"])
            check_type(argname="argument diff", value=diff, expected_type=type_hints["diff"])
            check_type(argname="argument synth", value=synth, expected_type=type_hints["synth"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "deploy": deploy,
            "diff": diff,
            "synth": synth,
        }

    @builtins.property
    def deploy(self) -> typing.List[DeployWorkflowConfig]:
        '''Configuration for the deploy workflow.'''
        result = self._values.get("deploy")
        assert result is not None, "Required property 'deploy' is missing"
        return typing.cast(typing.List[DeployWorkflowConfig], result)

    @builtins.property
    def diff(self) -> typing.List[DiffWorkflowConfig]:
        '''Configuration for the diff workflow.'''
        result = self._values.get("diff")
        assert result is not None, "Required property 'diff' is missing"
        return typing.cast(typing.List[DiffWorkflowConfig], result)

    @builtins.property
    def synth(self) -> "SynthWorkflowConfig":
        '''Configuration for the synth workflow.'''
        result = self._values.get("synth")
        assert result is not None, "Required property 'synth' is missing"
        return typing.cast("SynthWorkflowConfig", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GitHubWorkflowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GithubWorkflow(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.GithubWorkflow",
):
    def __init__(self, json: typing.Mapping[typing.Any, typing.Any]) -> None:
        '''
        :param json: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3923cfcb617f1c1f17d022bb3436263a7c98cdcb87f419363015fb8520b511d6)
            check_type(argname="argument json", value=json, expected_type=type_hints["json"])
        jsii.create(self.__class__, self, [json])

    @jsii.member(jsii_name="patch")
    def patch(self, *ops: "Patch") -> "GithubWorkflow":
        '''Applies a set of JSON-Patch (RFC-6902) operations to this object and returns the result.

        :param ops: The operations to apply.

        :return: The result object
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49ff91c791fec0d9e19de3f5d1c58b5d0e0e2045aeed51944132881cecfefa62)
            check_type(argname="argument ops", value=ops, expected_type=typing.Tuple[type_hints["ops"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast("GithubWorkflow", jsii.invoke(self, "patch", [*ops]))

    @builtins.property
    @jsii.member(jsii_name="json")
    def json(self) -> typing.Mapping[typing.Any, typing.Any]:
        return typing.cast(typing.Mapping[typing.Any, typing.Any], jsii.get(self, "json"))

    @json.setter
    def json(self, value: typing.Mapping[typing.Any, typing.Any]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22f05ed853a2e74dee0193a62770b3ae51bb4f3b85b9efbd5d32135798819a32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "json", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="cdk-express-pipeline.GithubWorkflowFile",
    jsii_struct_bases=[],
    name_mapping={"content": "content", "file_name": "fileName"},
)
class GithubWorkflowFile:
    def __init__(self, *, content: GithubWorkflow, file_name: builtins.str) -> None:
        '''
        :param content: 
        :param file_name: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__038bf0270c6ca55596a013a4a31894e79899942811087d804768f4ed4ba3d4e2)
            check_type(argname="argument content", value=content, expected_type=type_hints["content"])
            check_type(argname="argument file_name", value=file_name, expected_type=type_hints["file_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "content": content,
            "file_name": file_name,
        }

    @builtins.property
    def content(self) -> GithubWorkflow:
        result = self._values.get("content")
        assert result is not None, "Required property 'content' is missing"
        return typing.cast(GithubWorkflow, result)

    @builtins.property
    def file_name(self) -> builtins.str:
        result = self._values.get("file_name")
        assert result is not None, "Required property 'file_name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GithubWorkflowFile(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="cdk-express-pipeline.IExpressStack")
class IExpressStack(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stack identifier which is a combination of the wave, stage and stack id.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="stage")
    def stage(self) -> "ExpressStage":
        '''The stage that the stack belongs to.'''
        ...

    @stage.setter
    def stage(self, value: "ExpressStage") -> None:
        ...

    @jsii.member(jsii_name="addExpressDependency")
    def add_express_dependency(
        self,
        target: "ExpressStack",
        reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Add a dependency between this stack and another ExpressStack.

        This can be used to define dependencies between any two stacks within an

        :param target: The ``ExpressStack`` to depend on.
        :param reason: The reason for the dependency.
        '''
        ...

    @jsii.member(jsii_name="expressDependencies")
    def express_dependencies(self) -> typing.List["ExpressStack"]:
        '''The ExpressStack dependencies of the stack.'''
        ...


class _IExpressStackProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-express-pipeline.IExpressStack"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stack identifier which is a combination of the wave, stage and stack id.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76bd73c874b49b4683b044d917cc6800ed471f2b41d3164b902c206407432cbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stage")
    def stage(self) -> "ExpressStage":
        '''The stage that the stack belongs to.'''
        return typing.cast("ExpressStage", jsii.get(self, "stage"))

    @stage.setter
    def stage(self, value: "ExpressStage") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61a812768afc62205a9db0f1f9d01095658800d0cc43087913d4c1645cde7bdd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stage", value) # pyright: ignore[reportArgumentType]

    @jsii.member(jsii_name="addExpressDependency")
    def add_express_dependency(
        self,
        target: "ExpressStack",
        reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Add a dependency between this stack and another ExpressStack.

        This can be used to define dependencies between any two stacks within an

        :param target: The ``ExpressStack`` to depend on.
        :param reason: The reason for the dependency.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a14719acbf68f0fd518f950b2dd5d2922f8e4c9c9273c2f85d05589af97f191)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument reason", value=reason, expected_type=type_hints["reason"])
        return typing.cast(None, jsii.invoke(self, "addExpressDependency", [target, reason]))

    @jsii.member(jsii_name="expressDependencies")
    def express_dependencies(self) -> typing.List["ExpressStack"]:
        '''The ExpressStack dependencies of the stack.'''
        return typing.cast(typing.List["ExpressStack"], jsii.invoke(self, "expressDependencies", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExpressStack).__jsii_proxy_class__ = lambda : _IExpressStackProxy


@jsii.interface(jsii_type="cdk-express-pipeline.IExpressStage")
class IExpressStage(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stage identifier.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List["ExpressStack"]:
        '''The stacks in the stage.'''
        ...

    @stacks.setter
    def stacks(self, value: typing.List["ExpressStack"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="wave")
    def wave(self) -> "ExpressWave":
        '''The wave that the stage belongs to.'''
        ...

    @wave.setter
    def wave(self, value: "ExpressWave") -> None:
        ...


class _IExpressStageProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-express-pipeline.IExpressStage"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stage identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbca333d17cf67f3ebc52a25d3e08fdc38766f46ae2bcaeff4c01e2edbbd5dce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List["ExpressStack"]:
        '''The stacks in the stage.'''
        return typing.cast(typing.List["ExpressStack"], jsii.get(self, "stacks"))

    @stacks.setter
    def stacks(self, value: typing.List["ExpressStack"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d28e54cfe0e98d05cd17fa7ea13e156a82d091df55640c4094698ec7e78ed884)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stacks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wave")
    def wave(self) -> "ExpressWave":
        '''The wave that the stage belongs to.'''
        return typing.cast("ExpressWave", jsii.get(self, "wave"))

    @wave.setter
    def wave(self, value: "ExpressWave") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce620906fddfafba1ff8377098c5f9c35ada5694e2e5c6f9d15368e7d1d4c517)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wave", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExpressStage).__jsii_proxy_class__ = lambda : _IExpressStageProxy


@jsii.interface(jsii_type="cdk-express-pipeline.IExpressStageLegacy")
class IExpressStageLegacy(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stage identifier.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List[_aws_cdk_ceddda9d.Stack]:
        '''The stacks in the stage.'''
        ...

    @stacks.setter
    def stacks(self, value: typing.List[_aws_cdk_ceddda9d.Stack]) -> None:
        ...


class _IExpressStageLegacyProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-express-pipeline.IExpressStageLegacy"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stage identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fdf2493af932e5d33d989d572f161b8c998d0298e6a848f0a7af5edeca7b052)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List[_aws_cdk_ceddda9d.Stack]:
        '''The stacks in the stage.'''
        return typing.cast(typing.List[_aws_cdk_ceddda9d.Stack], jsii.get(self, "stacks"))

    @stacks.setter
    def stacks(self, value: typing.List[_aws_cdk_ceddda9d.Stack]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fffd047542b1ad122d53335fcab6ee350d782b3038d2efbf3f05152a18e8559c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stacks", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExpressStageLegacy).__jsii_proxy_class__ = lambda : _IExpressStageLegacyProxy


@jsii.interface(jsii_type="cdk-express-pipeline.IExpressWave")
class IExpressWave(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The wave identifier.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        '''Separator between the wave, stage and stack ids that are concatenated to form the final stack id.'''
        ...

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List["ExpressStage"]:
        '''The ExpressStages in the wave.'''
        ...

    @stages.setter
    def stages(self, value: typing.List["ExpressStage"]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="sequentialStages")
    def sequential_stages(self) -> typing.Optional[builtins.bool]:
        '''If true, the stages in the wave will be executed sequentially.

        :default: false
        '''
        ...

    @sequential_stages.setter
    def sequential_stages(self, value: typing.Optional[builtins.bool]) -> None:
        ...

    @jsii.member(jsii_name="addStage")
    def add_stage(self, id: builtins.str) -> "ExpressStage":
        '''Add an ExpressStage to the wave.

        :param id: The ExpressStage identifier.
        '''
        ...


class _IExpressWaveProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-express-pipeline.IExpressWave"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The wave identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8030e0d36f67ca6d88248c3aebc00cb88a9491700acbd6c7d3e4f5f06dcff718)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        '''Separator between the wave, stage and stack ids that are concatenated to form the final stack id.'''
        return typing.cast(builtins.str, jsii.get(self, "separator"))

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2deeb751aa022d2277fc1af871b8a9419aaef6e789a22f82063f21230a6d03fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "separator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List["ExpressStage"]:
        '''The ExpressStages in the wave.'''
        return typing.cast(typing.List["ExpressStage"], jsii.get(self, "stages"))

    @stages.setter
    def stages(self, value: typing.List["ExpressStage"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c33defa4497d6fd82c65487c1c51107af3c835ae4d7e1216f929dd314edaca26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sequentialStages")
    def sequential_stages(self) -> typing.Optional[builtins.bool]:
        '''If true, the stages in the wave will be executed sequentially.

        :default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "sequentialStages"))

    @sequential_stages.setter
    def sequential_stages(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae1159ae328148533b46258d902359880ce2c3976c0b7e6fc201ec69c017e429)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sequentialStages", value) # pyright: ignore[reportArgumentType]

    @jsii.member(jsii_name="addStage")
    def add_stage(self, id: builtins.str) -> "ExpressStage":
        '''Add an ExpressStage to the wave.

        :param id: The ExpressStage identifier.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0c0680f13cf234d76dc5ad77fd9b99005e303ff37a88d475016ab8e65495bbf)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast("ExpressStage", jsii.invoke(self, "addStage", [id]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExpressWave).__jsii_proxy_class__ = lambda : _IExpressWaveProxy


@jsii.interface(jsii_type="cdk-express-pipeline.IExpressWaveLegacy")
class IExpressWaveLegacy(typing_extensions.Protocol):
    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The wave identifier.'''
        ...

    @id.setter
    def id(self, value: builtins.str) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List[IExpressStageLegacy]:
        '''The ExpressStages in the wave.'''
        ...

    @stages.setter
    def stages(self, value: typing.List[IExpressStageLegacy]) -> None:
        ...

    @builtins.property
    @jsii.member(jsii_name="sequentialStages")
    def sequential_stages(self) -> typing.Optional[builtins.bool]:
        '''If true, the stages in the wave will be executed sequentially.

        :default: false
        '''
        ...

    @sequential_stages.setter
    def sequential_stages(self, value: typing.Optional[builtins.bool]) -> None:
        ...


class _IExpressWaveLegacyProxy:
    __jsii_type__: typing.ClassVar[str] = "cdk-express-pipeline.IExpressWaveLegacy"

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The wave identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebcd93f3691046bc34c345a2d0c5fd123d149d6852a73f251c4a5caeef0b161a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List[IExpressStageLegacy]:
        '''The ExpressStages in the wave.'''
        return typing.cast(typing.List[IExpressStageLegacy], jsii.get(self, "stages"))

    @stages.setter
    def stages(self, value: typing.List[IExpressStageLegacy]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8bc3fea3bdc86a865ca6e2fcf12e74fb6190d42fb2b51e85f0be6ed539336b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sequentialStages")
    def sequential_stages(self) -> typing.Optional[builtins.bool]:
        '''If true, the stages in the wave will be executed sequentially.

        :default: false
        '''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "sequentialStages"))

    @sequential_stages.setter
    def sequential_stages(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__344bf89503483c6b8c5fcb2f9805b54198866f417be91cb3b67b3d568e301831)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sequentialStages", value) # pyright: ignore[reportArgumentType]

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IExpressWaveLegacy).__jsii_proxy_class__ = lambda : _IExpressWaveLegacyProxy


class JsonPatch(metaclass=jsii.JSIIMeta, jsii_type="cdk-express-pipeline.JsonPatch"):
    '''Utility for applying RFC-6902 JSON-Patch to a document.

    Use the the ``JsonPatch.apply(doc, ...ops)`` function to apply a set of
    operations to a JSON document and return the result.

    Operations can be created using the factory methods ``JsonPatch.add()``,
    ``JsonPatch.remove()``, etc.

    const output = JsonPatch.apply(input,
    JsonPatch.replace('/world/hi/there', 'goodbye'),
    JsonPatch.add('/world/foo/', 'boom'),
    JsonPatch.remove('/hello'),
    );
    '''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="add")
    @builtins.classmethod
    def add(cls, path: builtins.str, value: typing.Any) -> "Patch":
        '''Adds a value to an object or inserts it into an array.

        In the case of an
        array, the value is inserted before the given index. The - character can be
        used instead of an index to insert at the end of an array.

        :param path: -
        :param value: -

        Example::

            JsonPatch.add('/biscuits/1', { "name": "Ginger Nut" })
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e889f82d734296a9f0fc5b80c758f87482441af97e2f6881b76116f0713750d9)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Patch", jsii.sinvoke(cls, "add", [path, value]))

    @jsii.member(jsii_name="copy")
    @builtins.classmethod
    def copy(cls, from_: builtins.str, path: builtins.str) -> "Patch":
        '''Copies a value from one location to another within the JSON document.

        Both
        from and path are JSON Pointers.

        :param from_: -
        :param path: -

        Example::

            JsonPatch.copy('/biscuits/0', '/best_biscuit')
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__813b3a258d86b3573be493d4a4f1937b1dce819225438e9c68f4aa38f4c2096e)
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast("Patch", jsii.sinvoke(cls, "copy", [from_, path]))

    @jsii.member(jsii_name="move")
    @builtins.classmethod
    def move(cls, from_: builtins.str, path: builtins.str) -> "Patch":
        '''Moves a value from one location to the other.

        Both from and path are JSON Pointers.

        :param from_: -
        :param path: -

        Example::

            JsonPatch.move('/biscuits', '/cookies')
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34fb68007ee11bfe467e5b1f06ca9be4c08cea9c900d9ac6d607578c852e6e6f)
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast("Patch", jsii.sinvoke(cls, "move", [from_, path]))

    @jsii.member(jsii_name="remove")
    @builtins.classmethod
    def remove(cls, path: builtins.str) -> "Patch":
        '''Removes a value from an object or array.

        :param path: -

        Example::

            JsonPatch.remove('/biscuits/0')
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bc2803e74056c4dfba071084f24ac7dd182da2d46c8b000b79ce5f02cee5705)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast("Patch", jsii.sinvoke(cls, "remove", [path]))

    @jsii.member(jsii_name="replace")
    @builtins.classmethod
    def replace(cls, path: builtins.str, value: typing.Any) -> "Patch":
        '''Replaces a value.

        Equivalent to a “remove” followed by an “add”.

        :param path: -
        :param value: -

        Example::

            JsonPatch.replace('/biscuits/0/name', 'Chocolate Digestive')
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17ed71656eb191c64ead4dc6b43291a424f80bceabb5b77fcb37d4c4b8c97936)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Patch", jsii.sinvoke(cls, "replace", [path, value]))

    @jsii.member(jsii_name="test")
    @builtins.classmethod
    def test(cls, path: builtins.str, value: typing.Any) -> "Patch":
        '''Tests that the specified value is set in the document.

        If the test fails,
        then the patch as a whole should not apply.

        :param path: -
        :param value: -

        Example::

            JsonPatch.test('/best_biscuit/name', 'Choco Leibniz')
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70c17fdce4c05352755c8a52f7d062025f2bb0826dbd449a0d8992c92ca5e51b)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("Patch", jsii.sinvoke(cls, "test", [path, value]))

    @jsii.member(jsii_name="patch")
    def patch(self, document: typing.Any, *ops: "Patch") -> typing.Any:
        '''Applies a set of JSON-Patch (RFC-6902) operations to ``document`` and returns the result.

        :param document: The document to patch.
        :param ops: The operations to apply.

        :return: The result document
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebb90fc798a7a245a98f9531a4a6f7ca5fe9f20211bc9558257b92b2ea04b634)
            check_type(argname="argument document", value=document, expected_type=type_hints["document"])
            check_type(argname="argument ops", value=ops, expected_type=typing.Tuple[type_hints["ops"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(typing.Any, jsii.invoke(self, "patch", [document, *ops]))


@jsii.data_type(
    jsii_type="cdk-express-pipeline.MermaidDiagramOutput",
    jsii_struct_bases=[],
    name_mapping={"file_name": "fileName", "path": "path"},
)
class MermaidDiagramOutput:
    def __init__(
        self,
        *,
        file_name: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file_name: Must end in ``.md``. If not provided, defaults to cdk-express-pipeline-deployment-order.md.
        :param path: The path where the Mermaid diagram will be saved. If not provided defaults to root
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__caca80227433ac13947de383baf8167a009b64337177ebceb2f23878fe124840)
            check_type(argname="argument file_name", value=file_name, expected_type=type_hints["file_name"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if file_name is not None:
            self._values["file_name"] = file_name
        if path is not None:
            self._values["path"] = path

    @builtins.property
    def file_name(self) -> typing.Optional[builtins.str]:
        '''Must end in ``.md``. If not provided, defaults to cdk-express-pipeline-deployment-order.md.'''
        result = self._values.get("file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''The path where the Mermaid diagram will be saved.

        If not provided defaults to root
        '''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MermaidDiagramOutput(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.Patch",
    jsii_struct_bases=[],
    name_mapping={"op": "op", "path": "path", "from_": "from", "value": "value"},
)
class Patch:
    def __init__(
        self,
        *,
        op: builtins.str,
        path: builtins.str,
        from_: typing.Optional[builtins.str] = None,
        value: typing.Any = None,
    ) -> None:
        '''
        :param op: 
        :param path: 
        :param from_: 
        :param value: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fe7f0ac4df8801b436758db5c210377cc3da157971ec27286e0f9c78ea316ab)
            check_type(argname="argument op", value=op, expected_type=type_hints["op"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument from_", value=from_, expected_type=type_hints["from_"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "op": op,
            "path": path,
        }
        if from_ is not None:
            self._values["from_"] = from_
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def op(self) -> builtins.str:
        result = self._values.get("op")
        assert result is not None, "Required property 'op' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path(self) -> builtins.str:
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def from_(self) -> typing.Optional[builtins.str]:
        result = self._values.get("from_")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Any:
        result = self._values.get("value")
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Patch(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.SynthWorkflowConfig",
    jsii_struct_bases=[],
    name_mapping={"build_config": "buildConfig", "commands": "commands"},
)
class SynthWorkflowConfig:
    def __init__(
        self,
        *,
        build_config: typing.Union[BuildConfig, typing.Dict[builtins.str, typing.Any]],
        commands: typing.Sequence[typing.Mapping[builtins.str, builtins.str]],
    ) -> None:
        '''
        :param build_config: Configuration for the build workflow.
        :param commands: Commands to run for synthesis.
        '''
        if isinstance(build_config, dict):
            build_config = BuildConfig(**build_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04546b59d0caef85d626030a6e0a441f23d5fb05cabb5e49cfda6fbf80c226ad)
            check_type(argname="argument build_config", value=build_config, expected_type=type_hints["build_config"])
            check_type(argname="argument commands", value=commands, expected_type=type_hints["commands"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "build_config": build_config,
            "commands": commands,
        }

    @builtins.property
    def build_config(self) -> BuildConfig:
        '''Configuration for the build workflow.'''
        result = self._values.get("build_config")
        assert result is not None, "Required property 'build_config' is missing"
        return typing.cast(BuildConfig, result)

    @builtins.property
    def commands(self) -> typing.List[typing.Mapping[builtins.str, builtins.str]]:
        '''Commands to run for synthesis.'''
        result = self._values.get("commands")
        assert result is not None, "Required property 'commands' is missing"
        return typing.cast(typing.List[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SynthWorkflowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.WorkflowLocation",
    jsii_struct_bases=[],
    name_mapping={"path": "path"},
)
class WorkflowLocation:
    def __init__(self, *, path: builtins.str) -> None:
        '''
        :param path: The path of the workflow to call before synthesis.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__201aead098a7134c6fd7dcb35cef32abfc1e2be9abfbca91e28a062d7541627e)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
        }

    @builtins.property
    def path(self) -> builtins.str:
        '''The path of the workflow to call before synthesis.'''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkflowLocation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.WorkflowTriggers",
    jsii_struct_bases=[],
    name_mapping={"pull_request": "pullRequest", "push": "push"},
)
class WorkflowTriggers:
    def __init__(
        self,
        *,
        pull_request: typing.Optional[typing.Union["WorkflowTriggersPullRequests", typing.Dict[builtins.str, typing.Any]]] = None,
        push: typing.Optional[typing.Union["WorkflowTriggersPush", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param pull_request: 
        :param push: 
        '''
        if isinstance(pull_request, dict):
            pull_request = WorkflowTriggersPullRequests(**pull_request)
        if isinstance(push, dict):
            push = WorkflowTriggersPush(**push)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a79785af7f44c5c832451175f3341cd5538fd42ec6de66f4f5750cdc30e4bc80)
            check_type(argname="argument pull_request", value=pull_request, expected_type=type_hints["pull_request"])
            check_type(argname="argument push", value=push, expected_type=type_hints["push"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if pull_request is not None:
            self._values["pull_request"] = pull_request
        if push is not None:
            self._values["push"] = push

    @builtins.property
    def pull_request(self) -> typing.Optional["WorkflowTriggersPullRequests"]:
        result = self._values.get("pull_request")
        return typing.cast(typing.Optional["WorkflowTriggersPullRequests"], result)

    @builtins.property
    def push(self) -> typing.Optional["WorkflowTriggersPush"]:
        result = self._values.get("push")
        return typing.cast(typing.Optional["WorkflowTriggersPush"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkflowTriggers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.WorkflowTriggersPullRequests",
    jsii_struct_bases=[],
    name_mapping={"branches": "branches"},
)
class WorkflowTriggersPullRequests:
    def __init__(
        self,
        *,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param branches: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26b6341660e3e70454386c5ce9a951fa0c7e59e59ade150cb48489e1eb584a4a)
            check_type(argname="argument branches", value=branches, expected_type=type_hints["branches"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if branches is not None:
            self._values["branches"] = branches

    @builtins.property
    def branches(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("branches")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkflowTriggersPullRequests(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-express-pipeline.WorkflowTriggersPush",
    jsii_struct_bases=[],
    name_mapping={"branches": "branches"},
)
class WorkflowTriggersPush:
    def __init__(
        self,
        *,
        branches: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param branches: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcbae0f217bbe05c16c45d14f261a43d5190abbe7a105bc981ed007bdc9774e8)
            check_type(argname="argument branches", value=branches, expected_type=type_hints["branches"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if branches is not None:
            self._values["branches"] = branches

    @builtins.property
    def branches(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("branches")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkflowTriggersPush(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IExpressStack)
class ExpressStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.ExpressStack",
):
    '''A CDK Express Pipeline Stack that belongs to an ExpressStage.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        stage: "ExpressStage",
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Constructs a new instance of the ExpressStack class.

        :param scope: The parent of this stack, usually an ``App`` but could be any construct.
        :param id: The stack identifier which will be used to construct the final id as a combination of the wave, stage and stack id.
        :param stage: The stage that the stack belongs to.
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Stack tags that will be applied to all the taggable resources and the stack itself. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15a9a33311b5aa41f122528e87925d8662e0815e5f09d7988e374cfdea050a91)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument stage", value=stage, expected_type=type_hints["stage"])
        stack_props = _aws_cdk_ceddda9d.StackProps(
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            permissions_boundary=permissions_boundary,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, stage, stack_props])

    @jsii.member(jsii_name="addDependency")
    def add_dependency(
        self,
        target: _aws_cdk_ceddda9d.Stack,
        reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Use ``addDependency`` for dependencies between stacks in an ExpressStage.

        Otherwise, use ``addExpressDependency``
        to construct the Pipeline of stacks between Waves and Stages.

        :param target: -
        :param reason: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcc587ab6bc13caffa524be9c0320a53ca9f80c4fc7c757ceffb0008ac347573)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument reason", value=reason, expected_type=type_hints["reason"])
        return typing.cast(None, jsii.invoke(self, "addDependency", [target, reason]))

    @jsii.member(jsii_name="addExpressDependency")
    def add_express_dependency(
        self,
        target: "ExpressStack",
        reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Only use to create dependencies between Stacks in Waves and Stages for building the Pipeline, where having cyclic dependencies is not possible.

        If the ``addExpressDependency`` is used outside the Pipeline construction,
        it will not be safe. Use ``addDependency`` to create stack dependency within the same Stage.

        :param target: -
        :param reason: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__879d590ae5362b889422ff44e98e8fdc081b30ab75c3f73bb791f1e59cffa2be)
            check_type(argname="argument target", value=target, expected_type=type_hints["target"])
            check_type(argname="argument reason", value=reason, expected_type=type_hints["reason"])
        return typing.cast(None, jsii.invoke(self, "addExpressDependency", [target, reason]))

    @jsii.member(jsii_name="expressDependencies")
    def express_dependencies(self) -> typing.List["ExpressStack"]:
        '''The ExpressStack dependencies of the stack.'''
        return typing.cast(typing.List["ExpressStack"], jsii.invoke(self, "expressDependencies", []))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stack identifier which is a combination of the wave, stage and stack id.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a767759dfa5395be6ecc01266961a9c2cc361036411cc35372ee6e11029546c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stage")
    def stage(self) -> "ExpressStage":
        '''The stage that the stack belongs to.'''
        return typing.cast("ExpressStage", jsii.get(self, "stage"))

    @stage.setter
    def stage(self, value: "ExpressStage") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e958c9ef72a2d0c3aaf0f9f1a60e0b6201b1633c81a640e71ca2bbe7f16654f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stage", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IExpressStage)
class ExpressStage(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.ExpressStage",
):
    '''A CDK Express Pipeline Stage that belongs to an ExpressWave.'''

    def __init__(
        self,
        id: builtins.str,
        wave: "ExpressWave",
        stacks: typing.Optional[typing.Sequence[ExpressStack]] = None,
    ) -> None:
        '''Constructs a new instance of the ExpressStage class.

        :param id: The stage identifier.
        :param wave: The wave that the stage belongs to.
        :param stacks: The ExpressStacks in the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__245ca2826c9b997f2790635ddcfbef04762bc8a2022332e01afc13b949cf70a4)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument wave", value=wave, expected_type=type_hints["wave"])
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
        jsii.create(self.__class__, self, [id, wave, stacks])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stage identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85b05051a77c643d3ed8a27735fdb1c5115fb33b71da08b5137bf934b65ebe1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List[ExpressStack]:
        '''The stacks in the stage.'''
        return typing.cast(typing.List[ExpressStack], jsii.get(self, "stacks"))

    @stacks.setter
    def stacks(self, value: typing.List[ExpressStack]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e05ff1a3d72f333ec26c5d8730168d1024b024fab396ec5decbb16ef55ecdd68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stacks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wave")
    def wave(self) -> "ExpressWave":
        '''The wave that the stage belongs to.'''
        return typing.cast("ExpressWave", jsii.get(self, "wave"))

    @wave.setter
    def wave(self, value: "ExpressWave") -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7663ce522608a1a19b5783485ae032e41251aa3bcaf50c25d7f5601587b2c86d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wave", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IExpressStageLegacy)
class ExpressStageLegacy(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.ExpressStageLegacy",
):
    '''A stage that holds stacks.'''

    def __init__(
        self,
        id: builtins.str,
        stacks: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.Stack]] = None,
    ) -> None:
        '''
        :param id: The stage identifier.
        :param stacks: The stacks in the stage.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef6fafe372848c826b5095466be599af161c0ef85262c4461c5b15946d416d8a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument stacks", value=stacks, expected_type=type_hints["stacks"])
        jsii.create(self.__class__, self, [id, stacks])

    @jsii.member(jsii_name="addStack")
    def add_stack(self, stack: _aws_cdk_ceddda9d.Stack) -> _aws_cdk_ceddda9d.Stack:
        '''Add a stack to the stage.

        :param stack: The stack to add.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c894af91effb498dcc85f4ce0d7c1ea7cc88b0e9ce46cd0afbe5faba127dcd9a)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        return typing.cast(_aws_cdk_ceddda9d.Stack, jsii.invoke(self, "addStack", [stack]))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The stage identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf3eb70b31883db55c7481c3af5635274ea0b531152ffc77fbe240d4cf471109)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stacks")
    def stacks(self) -> typing.List[_aws_cdk_ceddda9d.Stack]:
        '''The stacks in the stage.'''
        return typing.cast(typing.List[_aws_cdk_ceddda9d.Stack], jsii.get(self, "stacks"))

    @stacks.setter
    def stacks(self, value: typing.List[_aws_cdk_ceddda9d.Stack]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4560b751b8175d35b73d56b09336c93f3b65806421e5136ac4b9479b20d4fded)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stacks", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IExpressWave)
class ExpressWave(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.ExpressWave",
):
    '''A CDK Express Pipeline Wave that contains ExpressStages.'''

    def __init__(
        self,
        id: builtins.str,
        separator: typing.Optional[builtins.str] = None,
        sequential_stages: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Constructs a new instance of the ExpressWave class.

        :param id: The wave identifier.
        :param separator: Separator between the wave, stage and stack ids that are concatenated to form the stack id. Default: '_'.
        :param sequential_stages: If true, the stages in the wave will be executed sequentially. Default: false.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2d5f3923a6b2ec80e7126dcf3fee4db4c4302e23528b8f1a6b804dbcd52b1bd)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument separator", value=separator, expected_type=type_hints["separator"])
            check_type(argname="argument sequential_stages", value=sequential_stages, expected_type=type_hints["sequential_stages"])
        jsii.create(self.__class__, self, [id, separator, sequential_stages])

    @jsii.member(jsii_name="addStage")
    def add_stage(self, id: builtins.str) -> ExpressStage:
        '''Add an ExpressStage to the wave.

        :param id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2483221f4b80a77d7fb5425bb01e862bb0faa20975c01571285867e7ebac289a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(ExpressStage, jsii.invoke(self, "addStage", [id]))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The wave identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26db5d9a6d2445284b7c8d5a9e1f799dd10cda56d628bfa4a2a86e736e5b5f5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="separator")
    def separator(self) -> builtins.str:
        '''Separator between the wave, stage and stack ids that are concatenated to form the final stack id.'''
        return typing.cast(builtins.str, jsii.get(self, "separator"))

    @separator.setter
    def separator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d5854ca09bf38f246ea0ad1547c742b4d85ac21de4ecdd25f7fde0b74cee485)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "separator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List[ExpressStage]:
        '''The ExpressStages in the wave.'''
        return typing.cast(typing.List[ExpressStage], jsii.get(self, "stages"))

    @stages.setter
    def stages(self, value: typing.List[ExpressStage]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__397c6edf3478bfddcdbbc65faf7cf101e55552e8c9866bcc82db7287aa7e3727)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sequentialStages")
    def sequential_stages(self) -> typing.Optional[builtins.bool]:
        '''If true, the stages in the wave will be executed sequentially.'''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "sequentialStages"))

    @sequential_stages.setter
    def sequential_stages(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faca2817a2891ad9c62ca6c4294f0d2c4e09a89632dd03f8a2770e04ce81559d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sequentialStages", value) # pyright: ignore[reportArgumentType]


@jsii.implements(IExpressWaveLegacy)
class ExpressWaveLegacy(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-express-pipeline.ExpressWaveLegacy",
):
    '''A CDK Express Pipeline Legacy Wave that contains Legacy Stages.'''

    def __init__(
        self,
        id: builtins.str,
        sequential_stages: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Constructs a new instance of the ExpressWaveLegacy class.

        :param id: The wave identifier.
        :param sequential_stages: If true, the stages in the wave will be executed sequentially. Default: false.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0081ffdae64cce4db9c69087d8b66bb2d1dadbd8afbb7316e0b3bf8c9efbb03)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument sequential_stages", value=sequential_stages, expected_type=type_hints["sequential_stages"])
        jsii.create(self.__class__, self, [id, sequential_stages])

    @jsii.member(jsii_name="addStage")
    def add_stage(self, id: builtins.str) -> ExpressStageLegacy:
        '''Add a stage to the wave.

        :param id: The stage identifier.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a5c818dec4565e93efada7052a99392254569073240c5aa57b5dd41234ce08a)
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(ExpressStageLegacy, jsii.invoke(self, "addStage", [id]))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        '''The wave identifier.'''
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77354438e2a204945817e7e42750078579440a11efd1bc3059037d1a389dbf4b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stages")
    def stages(self) -> typing.List[IExpressStageLegacy]:
        '''The ExpressStages in the wave.'''
        return typing.cast(typing.List[IExpressStageLegacy], jsii.get(self, "stages"))

    @stages.setter
    def stages(self, value: typing.List[IExpressStageLegacy]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e46f4bd7d8ca47367b9b065564e04c58819d2f62dc94c8e21d96cab827ad27cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sequentialStages")
    def sequential_stages(self) -> typing.Optional[builtins.bool]:
        '''If true, the stages in the wave will be executed sequentially.'''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "sequentialStages"))

    @sequential_stages.setter
    def sequential_stages(self, value: typing.Optional[builtins.bool]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfb40afb352b1f780efc7514fb88ca08543b06d925f6ba10e33a7afa07d236db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sequentialStages", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "BuildConfig",
    "CdkExpressPipeline",
    "CdkExpressPipelineLegacy",
    "CdkExpressPipelineProps",
    "DeployWorkflowConfig",
    "DiffWorkflowConfig",
    "ExpressStack",
    "ExpressStage",
    "ExpressStageLegacy",
    "ExpressWave",
    "ExpressWaveLegacy",
    "ExpressWaveProps",
    "GitHubWorkflowConfig",
    "GithubWorkflow",
    "GithubWorkflowFile",
    "IExpressStack",
    "IExpressStage",
    "IExpressStageLegacy",
    "IExpressWave",
    "IExpressWaveLegacy",
    "JsonPatch",
    "MermaidDiagramOutput",
    "Patch",
    "SynthWorkflowConfig",
    "WorkflowLocation",
    "WorkflowTriggers",
    "WorkflowTriggersPullRequests",
    "WorkflowTriggersPush",
]

publication.publish()

def _typecheckingstub__176a33dbfec3fbf84c7f09cd7d5fa47dc7938b65faf1fefd2a2e277c8b10b538(
    *,
    type: builtins.str,
    workflow: typing.Optional[typing.Union[WorkflowLocation, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51d5a812c29abca46e9446db3e0acfaedb3fb0f70a5ccbc26b8b26b62c731b30(
    id: builtins.str,
    sequential_stages: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e284e6bc2289754ab5a16d412952ff0c2b3c0f4ae78655914206f911311579c0(
    git_hub_workflow_config: typing.Union[GitHubWorkflowConfig, typing.Dict[builtins.str, typing.Any]],
    save_to_files: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48596730e21a3fe0e78a5e73d024ad054e1679fbe0d63f873eb81c728a6fc0d6(
    waves: typing.Sequence[IExpressWave],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e18d77fb9496cb5fdeabb0fe5a14c3dcd08b7a4747694ac0a799b01dfa105a34(
    waves: typing.Sequence[IExpressWave],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a545be0c7f0244a8cedbc9796c6c38f57f873c3c1ba9bb23a76f5d8f63bfafa(
    workflows: typing.Sequence[typing.Union[GithubWorkflowFile, typing.Dict[builtins.str, typing.Any]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddf3f54429b9cebdd63080df8e42a8f0bee80ea5889f7848d8110f99befcf433(
    waves: typing.Optional[typing.Sequence[IExpressWave]] = None,
    print: typing.Optional[builtins.bool] = None,
    *,
    file_name: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e78d8fa8554a29ac59173413b98062741ae83aeb4754f02a80c85c27e16d8ce(
    waves: typing.Optional[typing.Sequence[IExpressWaveLegacy]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58733341409ff8a6c60fbf06de891a31f81f41cf55e7503aaa0238ee46ff5166(
    id: builtins.str,
    sequential_stages: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1ef4d18ff1ca1a7788d1801361a996c26480f2387d3a28be69812108f489380(
    waves: typing.Sequence[IExpressWaveLegacy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d22fe922729d650ca61abf0f4568bb8cbafe791434481f3e0cce74d098f785e(
    waves: typing.Sequence[IExpressWaveLegacy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c7d8bd5a65c1437ed17046edfb50f14e1f2b8f73c9db08927132a10f37d409d(
    waves: typing.Optional[typing.Sequence[IExpressWaveLegacy]] = None,
    print: typing.Optional[builtins.bool] = None,
    *,
    file_name: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54082bd27a8ceffd74f1b6a0cb05b3bbcf4ffa9ada94c72e52e645687ad4ad5b(
    value: typing.List[IExpressWaveLegacy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc99a79d5da23f439f19b4717a315983fa455ec2ae7d0300ac3d7381d5892205(
    *,
    separator: typing.Optional[builtins.str] = None,
    waves: typing.Optional[typing.Sequence[ExpressWave]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__064ff6a399a517de1d9d8831492460b92378a4013ef6125878a1c1553dab6e74(
    *,
    assume_region: builtins.str,
    assume_role_arn: builtins.str,
    commands: typing.Sequence[typing.Mapping[builtins.str, builtins.str]],
    on: typing.Union[WorkflowTriggers, typing.Dict[builtins.str, typing.Any]],
    stack_selector: builtins.str,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fd8d22f0c989f84b5e91067c258f24562fc4d3b5c471e9302c3fd36c7c66492(
    *,
    assume_region: builtins.str,
    assume_role_arn: builtins.str,
    commands: typing.Sequence[typing.Mapping[builtins.str, builtins.str]],
    on: typing.Union[WorkflowTriggers, typing.Dict[builtins.str, typing.Any]],
    stack_selector: builtins.str,
    id: typing.Optional[builtins.str] = None,
    write_as_comment: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d91dc79595e990d6da1a185afde4e65465da1f5dc12abd5220e16803db5481a2(
    *,
    id: builtins.str,
    separator: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a08064d282d091b65891b01b014a0a8a260163ad7f73ec21450a321e2a8b285(
    *,
    deploy: typing.Sequence[typing.Union[DeployWorkflowConfig, typing.Dict[builtins.str, typing.Any]]],
    diff: typing.Sequence[typing.Union[DiffWorkflowConfig, typing.Dict[builtins.str, typing.Any]]],
    synth: typing.Union[SynthWorkflowConfig, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3923cfcb617f1c1f17d022bb3436263a7c98cdcb87f419363015fb8520b511d6(
    json: typing.Mapping[typing.Any, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49ff91c791fec0d9e19de3f5d1c58b5d0e0e2045aeed51944132881cecfefa62(
    *ops: Patch,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22f05ed853a2e74dee0193a62770b3ae51bb4f3b85b9efbd5d32135798819a32(
    value: typing.Mapping[typing.Any, typing.Any],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__038bf0270c6ca55596a013a4a31894e79899942811087d804768f4ed4ba3d4e2(
    *,
    content: GithubWorkflow,
    file_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76bd73c874b49b4683b044d917cc6800ed471f2b41d3164b902c206407432cbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61a812768afc62205a9db0f1f9d01095658800d0cc43087913d4c1645cde7bdd(
    value: ExpressStage,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a14719acbf68f0fd518f950b2dd5d2922f8e4c9c9273c2f85d05589af97f191(
    target: ExpressStack,
    reason: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbca333d17cf67f3ebc52a25d3e08fdc38766f46ae2bcaeff4c01e2edbbd5dce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d28e54cfe0e98d05cd17fa7ea13e156a82d091df55640c4094698ec7e78ed884(
    value: typing.List[ExpressStack],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce620906fddfafba1ff8377098c5f9c35ada5694e2e5c6f9d15368e7d1d4c517(
    value: ExpressWave,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fdf2493af932e5d33d989d572f161b8c998d0298e6a848f0a7af5edeca7b052(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fffd047542b1ad122d53335fcab6ee350d782b3038d2efbf3f05152a18e8559c(
    value: typing.List[_aws_cdk_ceddda9d.Stack],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8030e0d36f67ca6d88248c3aebc00cb88a9491700acbd6c7d3e4f5f06dcff718(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2deeb751aa022d2277fc1af871b8a9419aaef6e789a22f82063f21230a6d03fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c33defa4497d6fd82c65487c1c51107af3c835ae4d7e1216f929dd314edaca26(
    value: typing.List[ExpressStage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae1159ae328148533b46258d902359880ce2c3976c0b7e6fc201ec69c017e429(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0c0680f13cf234d76dc5ad77fd9b99005e303ff37a88d475016ab8e65495bbf(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebcd93f3691046bc34c345a2d0c5fd123d149d6852a73f251c4a5caeef0b161a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8bc3fea3bdc86a865ca6e2fcf12e74fb6190d42fb2b51e85f0be6ed539336b3(
    value: typing.List[IExpressStageLegacy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__344bf89503483c6b8c5fcb2f9805b54198866f417be91cb3b67b3d568e301831(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e889f82d734296a9f0fc5b80c758f87482441af97e2f6881b76116f0713750d9(
    path: builtins.str,
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__813b3a258d86b3573be493d4a4f1937b1dce819225438e9c68f4aa38f4c2096e(
    from_: builtins.str,
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34fb68007ee11bfe467e5b1f06ca9be4c08cea9c900d9ac6d607578c852e6e6f(
    from_: builtins.str,
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bc2803e74056c4dfba071084f24ac7dd182da2d46c8b000b79ce5f02cee5705(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17ed71656eb191c64ead4dc6b43291a424f80bceabb5b77fcb37d4c4b8c97936(
    path: builtins.str,
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70c17fdce4c05352755c8a52f7d062025f2bb0826dbd449a0d8992c92ca5e51b(
    path: builtins.str,
    value: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebb90fc798a7a245a98f9531a4a6f7ca5fe9f20211bc9558257b92b2ea04b634(
    document: typing.Any,
    *ops: Patch,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caca80227433ac13947de383baf8167a009b64337177ebceb2f23878fe124840(
    *,
    file_name: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fe7f0ac4df8801b436758db5c210377cc3da157971ec27286e0f9c78ea316ab(
    *,
    op: builtins.str,
    path: builtins.str,
    from_: typing.Optional[builtins.str] = None,
    value: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04546b59d0caef85d626030a6e0a441f23d5fb05cabb5e49cfda6fbf80c226ad(
    *,
    build_config: typing.Union[BuildConfig, typing.Dict[builtins.str, typing.Any]],
    commands: typing.Sequence[typing.Mapping[builtins.str, builtins.str]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__201aead098a7134c6fd7dcb35cef32abfc1e2be9abfbca91e28a062d7541627e(
    *,
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a79785af7f44c5c832451175f3341cd5538fd42ec6de66f4f5750cdc30e4bc80(
    *,
    pull_request: typing.Optional[typing.Union[WorkflowTriggersPullRequests, typing.Dict[builtins.str, typing.Any]]] = None,
    push: typing.Optional[typing.Union[WorkflowTriggersPush, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26b6341660e3e70454386c5ce9a951fa0c7e59e59ade150cb48489e1eb584a4a(
    *,
    branches: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcbae0f217bbe05c16c45d14f261a43d5190abbe7a105bc981ed007bdc9774e8(
    *,
    branches: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15a9a33311b5aa41f122528e87925d8662e0815e5f09d7988e374cfdea050a91(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    stage: ExpressStage,
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcc587ab6bc13caffa524be9c0320a53ca9f80c4fc7c757ceffb0008ac347573(
    target: _aws_cdk_ceddda9d.Stack,
    reason: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__879d590ae5362b889422ff44e98e8fdc081b30ab75c3f73bb791f1e59cffa2be(
    target: ExpressStack,
    reason: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a767759dfa5395be6ecc01266961a9c2cc361036411cc35372ee6e11029546c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e958c9ef72a2d0c3aaf0f9f1a60e0b6201b1633c81a640e71ca2bbe7f16654f(
    value: ExpressStage,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__245ca2826c9b997f2790635ddcfbef04762bc8a2022332e01afc13b949cf70a4(
    id: builtins.str,
    wave: ExpressWave,
    stacks: typing.Optional[typing.Sequence[ExpressStack]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85b05051a77c643d3ed8a27735fdb1c5115fb33b71da08b5137bf934b65ebe1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e05ff1a3d72f333ec26c5d8730168d1024b024fab396ec5decbb16ef55ecdd68(
    value: typing.List[ExpressStack],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7663ce522608a1a19b5783485ae032e41251aa3bcaf50c25d7f5601587b2c86d(
    value: ExpressWave,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef6fafe372848c826b5095466be599af161c0ef85262c4461c5b15946d416d8a(
    id: builtins.str,
    stacks: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.Stack]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c894af91effb498dcc85f4ce0d7c1ea7cc88b0e9ce46cd0afbe5faba127dcd9a(
    stack: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf3eb70b31883db55c7481c3af5635274ea0b531152ffc77fbe240d4cf471109(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4560b751b8175d35b73d56b09336c93f3b65806421e5136ac4b9479b20d4fded(
    value: typing.List[_aws_cdk_ceddda9d.Stack],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2d5f3923a6b2ec80e7126dcf3fee4db4c4302e23528b8f1a6b804dbcd52b1bd(
    id: builtins.str,
    separator: typing.Optional[builtins.str] = None,
    sequential_stages: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2483221f4b80a77d7fb5425bb01e862bb0faa20975c01571285867e7ebac289a(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26db5d9a6d2445284b7c8d5a9e1f799dd10cda56d628bfa4a2a86e736e5b5f5a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d5854ca09bf38f246ea0ad1547c742b4d85ac21de4ecdd25f7fde0b74cee485(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__397c6edf3478bfddcdbbc65faf7cf101e55552e8c9866bcc82db7287aa7e3727(
    value: typing.List[ExpressStage],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faca2817a2891ad9c62ca6c4294f0d2c4e09a89632dd03f8a2770e04ce81559d(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0081ffdae64cce4db9c69087d8b66bb2d1dadbd8afbb7316e0b3bf8c9efbb03(
    id: builtins.str,
    sequential_stages: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a5c818dec4565e93efada7052a99392254569073240c5aa57b5dd41234ce08a(
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77354438e2a204945817e7e42750078579440a11efd1bc3059037d1a389dbf4b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e46f4bd7d8ca47367b9b065564e04c58819d2f62dc94c8e21d96cab827ad27cc(
    value: typing.List[IExpressStageLegacy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfb40afb352b1f780efc7514fb88ca08543b06d925f6ba10e33a7afa07d236db(
    value: typing.Optional[builtins.bool],
) -> None:
    """Type checking stubs"""
    pass
