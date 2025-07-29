/* ----------------------------------------------------------------- *
 * (C) Copyright IBM Corporation 2024.                               *
 *                                                                   *
 * The source code for this program is not published or otherwise    *
 * divested of its trade secrets, irrespective of what has been      *
 * deposited with the U.S. Copyright Office.                         *
 * ----------------------------------------------------------------- */
// SPDX-License-Identifier: Apache-2.0

package main

import (
	"os"
	// Import all Kubernetes client auth plugins (e.g. Azure, GCP, OIDC, etc.)
	// to ensure that exec-entrypoint and run can make use of them.
	"flag"
	"fmt"
	"runtime/pprof"

	"github.ibm.com/Michael-Honaker/kubernetes-lite/kubernetes_lite/go_wrapper/internal"
	"github.ibm.com/Michael-Honaker/kubernetes-lite/kubernetes_lite/go_wrapper/pkg/client"
	"github.ibm.com/Michael-Honaker/kubernetes-lite/kubernetes_lite/go_wrapper/pkg/envtest/server"
	"github.ibm.com/Michael-Honaker/kubernetes-lite/kubernetes_lite/go_wrapper/pkg/envtest/setup"
)

var cpuprofile = flag.String("cpuprofile", "", "write cpu profile to file")
var iterations = flag.Uint("iterations", 1, "How many iterations")

const crd_yaml = `{"apiVersion":"apiextensions.k8s.io/v1","kind":"CustomResourceDefinition","metadata":{"name":"perftests.rekanoh.com"},"spec":{"group":"rekanoh.com","versions":[{"name":"v1","served":true,"storage":true,"schema":{"openAPIV3Schema":{"type":"object","properties":{"spec":{"x-kubernetes-preserve-unknown-fields":true,"type":"object"}}}}}],"scope":"Namespaced","names":{"plural":"perftests","singular":"perftest","kind":"PerfTest","shortNames":["pt"]}}}`
const deployment_yaml = `{"kind":"PerfTest","apiVersion":"rekanoh.com/v1","metadata":{"name":"test-perf-obj","namespace":"default"},"spec":{"data":[{"_id":"67741876a08defd1573ec15b","index":0,"guid":"80f748f5-1a06-4fa4-8a5b-cb4795b60b7e","isActive":false,"balance":"$1,467.52","picture":"http://placehold.it/32x32","age":20,"eyeColor":"brown","name":"Kari Marquez","gender":"female","company":"SOLGAN","email":"karimarquez@solgan.com","phone":"+1 (970) 538-2175","address":"151 Aurelia Court, Waterford, Kentucky, 5502","about":"Aliquip ullamco laboris consequat id tempor enim qui ullamco enim dolore anim voluptate aliquip. Commodo proident magna cupidatat dolore. Sunt cupidatat duis minim ad cillum dolor aliqua consectetur nulla in in eiusmod commodo. Occaecat consequat consequat ex duis aliquip velit ea deserunt sint culpa sunt fugiat do. Elit mollit cupidatat esse dolore exercitation aliquip. Nisi culpa quis Lorem amet mollit velit enim ut consequat non anim do reprehenderit.\r\n","registered":"2017-01-21T06:23:53 +05:00","latitude":-46.856267,"longitude":85.778074,"tags":["dolor","incididunt","ipsum","incididunt","anim","reprehenderit","exercitation"],"friends":[{"id":0,"name":"Trujillo Mercado"},{"id":1,"name":"Evangelina Shelton"},{"id":2,"name":"Guzman Byers"}],"greeting":"Hello, Kari Marquez! You have 1 unread messages.","favoriteFruit":"strawberry"},{"_id":"677418765a7a84531cc272da","index":1,"guid":"2f4340a2-dc96-48e7-b447-88d9bb003224","isActive":false,"balance":"$1,509.60","picture":"http://placehold.it/32x32","age":25,"eyeColor":"green","name":"Lillian Rutledge","gender":"female","company":"ISBOL","email":"lillianrutledge@isbol.com","phone":"+1 (925) 405-2044","address":"577 Prospect Avenue, Dragoon, Virgin Islands, 9176","about":"Voluptate tempor id enim laboris magna officia pariatur irure deserunt ad aliqua officia magna. Veniam et nisi labore dolor quis ad dolore pariatur nulla magna duis anim pariatur ex. Do anim veniam duis veniam minim adipisicing id et minim. Et aliquip consequat fugiat cillum mollit eu laboris Lorem deserunt deserunt sit ut. Enim officia magna et ea dolore ad ad aliquip enim Lorem laborum sit veniam minim.\r\n","registered":"2020-09-14T10:30:31 +04:00","latitude":-58.12084,"longitude":-3.048845,"tags":["mollit","et","dolor","excepteur","eu","elit","anim"],"friends":[{"id":0,"name":"Willa Schultz"},{"id":1,"name":"Elisa Carrillo"},{"id":2,"name":"Catalina Buck"}],"greeting":"Hello, Lillian Rutledge! You have 8 unread messages.","favoriteFruit":"apple"},{"_id":"677418768eb1dd40c08c3e55","index":2,"guid":"f907ee8b-9db1-4ceb-a961-d0586e7f506e","isActive":true,"balance":"$2,343.82","picture":"http://placehold.it/32x32","age":34,"eyeColor":"brown","name":"Mueller Newman","gender":"male","company":"PYRAMIS","email":"muellernewman@pyramis.com","phone":"+1 (890) 497-3164","address":"513 Baughman Place, Ticonderoga, Virginia, 4404","about":"Sit eiusmod sint amet deserunt commodo ut elit esse. Sit ea anim non amet voluptate laboris cillum nostrud aliqua esse eu anim aute irure. Duis sit duis aute in duis fugiat nostrud irure irure pariatur amet ullamco voluptate.\r\n","registered":"2016-03-20T01:11:12 +04:00","latitude":89.476035,"longitude":56.832644,"tags":["do","consectetur","ipsum","aliqua","culpa","qui","sit"],"friends":[{"id":0,"name":"Geneva Merrill"},{"id":1,"name":"Murray Sharpe"},{"id":2,"name":"Priscilla Alvarado"}],"greeting":"Hello, Mueller Newman! You have 2 unread messages.","favoriteFruit":"banana"},{"_id":"677418760a0c551e5ca77883","index":3,"guid":"0c29410f-6a52-4cbc-b103-55733027a1b5","isActive":true,"balance":"$1,374.30","picture":"http://placehold.it/32x32","age":25,"eyeColor":"blue","name":"Trevino Reese","gender":"male","company":"BESTO","email":"trevinoreese@besto.com","phone":"+1 (824) 574-3956","address":"857 Putnam Avenue, Innsbrook, Texas, 6329","about":"Ipsum nostrud laborum magna ad. Labore occaecat amet nisi minim ut et est magna. Aute do commodo id exercitation. Anim ullamco minim culpa minim pariatur incididunt officia officia ea et irure incididunt eu. Culpa reprehenderit occaecat ullamco est consequat. Reprehenderit esse adipisicing nisi occaecat nostrud fugiat enim id non occaecat dolor culpa.\r\n","registered":"2020-12-11T09:43:58 +05:00","latitude":29.623109,"longitude":-133.728112,"tags":["ipsum","cupidatat","culpa","et","reprehenderit","veniam","magna"],"friends":[{"id":0,"name":"Shelby Robertson"},{"id":1,"name":"Riley Patton"},{"id":2,"name":"Vincent Berger"}],"greeting":"Hello, Trevino Reese! You have 2 unread messages.","favoriteFruit":"apple"},{"_id":"67741876408a32adf70bc0a6","index":4,"guid":"6c458784-8c69-4422-b841-a25cebcde654","isActive":false,"balance":"$1,101.89","picture":"http://placehold.it/32x32","age":40,"eyeColor":"brown","name":"Erna Shaffer","gender":"female","company":"CORIANDER","email":"ernashaffer@coriander.com","phone":"+1 (869) 421-2182","address":"241 Bleecker Street, Dunnavant, Arkansas, 805","about":"Fugiat anim tempor quis ullamco exercitation ut laborum quis dolore exercitation nisi consequat dolore nulla. Reprehenderit qui veniam nostrud nulla labore duis sunt eiusmod. Est sint aute minim adipisicing nostrud et irure ad laborum eiusmod magna tempor nisi laboris. Consectetur elit proident culpa anim eu elit reprehenderit eu aliquip eu non. Elit magna non laborum mollit magna mollit dolore elit Lorem culpa.\r\n","registered":"2021-04-26T12:24:52 +04:00","latitude":46.905742,"longitude":-0.835789,"tags":["nulla","excepteur","quis","veniam","nostrud","amet","culpa"],"friends":[{"id":0,"name":"Nelda King"},{"id":1,"name":"Wilder Mendoza"},{"id":2,"name":"Gaines Ware"}],"greeting":"Hello, Erna Shaffer! You have 7 unread messages.","favoriteFruit":"banana"},{"_id":"677418764e9abb4f90357cc4","index":5,"guid":"581791d9-d533-41cd-a199-57ffec8e26b9","isActive":true,"balance":"$1,947.45","picture":"http://placehold.it/32x32","age":33,"eyeColor":"green","name":"Travis Vaughan","gender":"male","company":"ZENSUS","email":"travisvaughan@zensus.com","phone":"+1 (930) 424-2428","address":"184 Juliana Place, Watrous, Georgia, 1821","about":"Laboris culpa reprehenderit eiusmod duis qui laboris tempor voluptate nisi officia. Occaecat irure commodo mollit et ullamco ad laboris. Do eu mollit consequat ea dolor laborum ex veniam laborum. Proident consequat mollit duis magna irure aliquip laborum in. Consectetur et aliquip do nulla esse. Exercitation culpa do ex labore nostrud. Est occaecat exercitation Lorem est anim non et anim ullamco qui.\r\n","registered":"2018-12-19T01:21:09 +05:00","latitude":-48.001737,"longitude":143.332702,"tags":["exercitation","labore","proident","irure","sunt","esse","nisi"],"friends":[{"id":0,"name":"Short Day"},{"id":1,"name":"Hood Hart"},{"id":2,"name":"Alston Coffey"}],"greeting":"Hello, Travis Vaughan! You have 9 unread messages.","favoriteFruit":"banana"},{"_id":"677418766c451647fbab9b65","index":6,"guid":"41742ad3-020b-4a14-a4a4-14388edd8d73","isActive":true,"balance":"$3,929.97","picture":"http://placehold.it/32x32","age":35,"eyeColor":"brown","name":"Mcbride Golden","gender":"male","company":"EMTRAC","email":"mcbridegolden@emtrac.com","phone":"+1 (952) 497-2540","address":"375 Eastern Parkway, Thatcher, New Hampshire, 5215","about":"Consequat est Lorem reprehenderit deserunt incididunt aliquip sunt voluptate qui laboris occaecat laboris. Velit est laborum pariatur anim occaecat consectetur aliquip nulla aliquip occaecat ipsum enim adipisicing pariatur. Exercitation consequat aliqua occaecat nulla cupidatat proident exercitation mollit aute amet. Ipsum consequat nostrud exercitation pariatur aliqua ea aute reprehenderit adipisicing nostrud. Lorem aliquip non elit reprehenderit cillum labore minim.\r\n","registered":"2018-04-13T02:59:16 +04:00","latitude":20.173958,"longitude":34.115592,"tags":["nostrud","adipisicing","culpa","sint","occaecat","pariatur","et"],"friends":[{"id":0,"name":"Mccray Landry"},{"id":1,"name":"Karyn Pollard"},{"id":2,"name":"Margret Vega"}],"greeting":"Hello, Mcbride Golden! You have 4 unread messages.","favoriteFruit":"apple"}]}}`

func main() {
	// Parse Flags before doing anything
	flag.Parse()

	setupResData, err := setup.SetupEnvTest([]byte{}, []byte(`["python3 -m setup","use","-p","path"]`))
	if err != nil {
		panic(err)
	}

	setupRes := setup.SetupEnvTestResult{}
	err = internal.Unmarshal(setupResData, &setupRes)
	if err != nil {
		panic(err)
	}

	path := setupRes.Stdout
	envtestServer, err := server.NewEnvTestEnvironmentWithPath(*path)
	if err != nil {
		panic(err)
	}

	cfg, err := envtestServer.Start()
	if err != nil {
		panic(err)
	}
	fmt.Println("Started EnvTest")

	dynClient, err := client.NewWrappedDynamicClientWithConfig(cfg, -1, 1000, "")
	if err != nil {
		panic(err)
	}
	fmt.Println("Constructed Client")

	crd_deploy_res, err := dynClient.Resource("apiextensions.k8s.io/v1", "CustomResourceDefinition")
	if err != nil {
		panic(err)
	}
	_, err = crd_deploy_res.Apply("perftests.rekanoh.com", []byte(crd_yaml), []byte(`{"fieldManager":"default"}`))
	fmt.Println("Applied CRD")

	deploy_res, err := dynClient.Resource("rekanoh.com/v1", "PerfTest")
	if err != nil {
		panic(err)
	}
	named_deploy_res := deploy_res.Namespace("default")
	fmt.Println("Constructed Client Resource")

	if *cpuprofile != "" {
		fmt.Println("Starting CPU Profile")
		f, err := os.Create(*cpuprofile)
		if err != nil {
			panic(err)
		}
		pprof.StartCPUProfile(f)
		defer pprof.StopCPUProfile()
	}

	for i := range *iterations {
		_, err = named_deploy_res.Apply("test-perf-obj", []byte(deployment_yaml), []byte(`{"fieldManager":"default"}`))
		if err != nil {
			panic(err)
		}
		fmt.Println("Applied Resource", i)
	}
}
